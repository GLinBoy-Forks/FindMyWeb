import uuid
import datetime

from pyargon2 import hash
from sqlmodel import Session, SQLModel, create_engine, desc, or_, select

from const import CONFIG
from database.exceptions import (
    AccessoryDoesntExist,
    AccessoryExists,
    UserDoesNotExist,
    UserExists,
)
from database.models import Accessory, Location, User


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(CONFIG.db.uri)
        SQLModel.metadata.create_all(self.engine)

    async def _encrypt_pwd(self, password: str) -> str:
        return hash(password, CONFIG.jwt.secret)

    async def _location_exists(self, location: Location) -> bool:
        statement = select(Location).where(Location.id == location.id)

        with Session(self.engine) as session:
            result = session.exec(statement)

            return len(result.all()) > 0

    async def _accessory_exists(self, accessory: Accessory) -> bool:
        statement = select(Accessory).where(
            or_(
                Accessory.private_key == accessory.private_key,
                Accessory.name == accessory.name,
            )
        )
        with Session(self.engine) as session:
            result = session.exec(statement)

            if len(list(result.all())) > 0:
                return True

        return False

    async def setup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def get_users(self) -> list[User]:
        statement = select(User)
        with Session(self.engine) as session:
            result = session.exec(statement)

            return list(result.all())

    async def get_user(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        with Session(self.engine) as session:
            results = session.exec(statement=statement)

            return results.one_or_none()

    async def get_user_by_id(self, id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == id)
        with Session(self.engine) as session:
            results = session.exec(statement=statement)

            return results.one_or_none()

    async def get_accessory_by_key(self, user: User, key: str) -> Accessory:
        statement = select(Accessory).where(
            Accessory.user_id == user.id, Accessory.private_key == key
        )
        with Session(self.engine) as session:
            results = session.exec(statement=statement)
            try:
                return results.one()
            except:
                raise AccessoryDoesntExist("Provided accessory doesn't exist")

    async def get_accessories_by_user(self, user: User) -> list[Accessory]:
        statement = select(Accessory).where(Accessory.user_id == user.id)
        with Session(self.engine) as session:
            results = session.exec(statement=statement)

            return list(results.all())

    async def get_accessory(self, user: User, name: str) -> Accessory | None:
        statement = select(Accessory).where(
            Accessory.name == name, Accessory.user_id == user.id
        )
        with Session(self.engine) as session:
            results = session.exec(statement=statement)

            return results.one_or_none()

    async def get_last_location(self, accessory: Accessory) -> Location | None:
        statement = (
            select(Location)
            .where(
                Location.accessory_key == accessory.private_key,
            )
            .order_by(desc(Location.timestamp))
            .limit(1)
        )
        with Session(self.engine) as session:
            results = session.exec(statement=statement)

            return results.one_or_none()

    async def get_locations(
        self,
        accessory: Accessory,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        limit: int | None,
    ) -> list[Location]:
        statement = (
            select(Location)
            .where(
                Location.accessory_key == accessory.private_key,
                Location.timestamp >= start_date,
                Location.timestamp <= end_date,
            )
            .order_by(desc(Location.timestamp))
            .limit(limit)
        )
        with Session(self.engine) as session:
            results = session.exec(statement=statement)

            return list(results.all())

    async def add_user(
        self, username: str, password: str, is_admin: bool = False
    ) -> User:
        if await self.get_user(username=username):
            raise UserExists("User already exists")

        new_user = User(
            username=username,
            password_hash=await self._encrypt_pwd(password=password),
            admin=is_admin,
        )
        with Session(self.engine) as session:
            session.add(new_user)
            session.commit()

            session.refresh(new_user)
        return new_user

    async def add_accessory(self, accessory: Accessory) -> Accessory:
        if await self._accessory_exists(accessory=accessory):
            raise AccessoryExists("Accessory already exists")

        with Session(self.engine) as session:
            session.add(accessory)
            session.commit()
            session.refresh(accessory)

        return accessory

    async def add_location(self, location: Location) -> Location | None:
        if await self._location_exists(location):
            return None
        with Session(self.engine) as session:
            session.add(location)
            session.commit()

            session.refresh(location)
        return location

    async def update_accessory(self, user: User, accessory: Accessory) -> Accessory:
        old_accessory = await self.get_accessory_by_key(user, accessory.private_key)
        if not old_accessory:
            raise AccessoryDoesntExist("Accessory doesn't exist")

        with Session(self.engine) as session:
            if old_accessory.name != accessory.name:
                old_accessory.name = accessory.name

            if old_accessory.icon != accessory.icon:
                old_accessory.icon = accessory.icon

            if old_accessory.color != accessory.color:
                old_accessory.color = accessory.color

            session.add(old_accessory)
            session.commit()
            session.refresh(old_accessory)

        return old_accessory

    async def update_user(self, user: User) -> User:
        with Session(self.engine) as session:
            session.add(user)
            session.commit()

            session.refresh(user)

        return user

    async def update_password(self, user: User, new_password: str) -> User:
        user.password_hash = await self._encrypt_pwd(new_password)
        with Session(self.engine) as session:
            session.add(user)
            session.commit()

            session.refresh(user)
        return user

    async def remove_accessory(self, accessory: Accessory) -> None:
        with Session(self.engine) as session:
            results = session.delete(accessory)
            session.commit()

    async def remove_user(self, username: str) -> None:
        with Session(self.engine) as session:
            user = await self.get_user(username=username)
            if not user:
                raise UserDoesNotExist("User does not exist")

            results = session.delete(user)
            session.commit()

    async def verify(self, user: User, password: str) -> bool:
        pwd_hash = await self._encrypt_pwd(password=password)

        return pwd_hash == user.password_hash
