from typing import TYPE_CHECKING, Union

from app.helpers import UNKNOW_PROVIDER_EXCEPTION
from app.models.accessory import AccessoryOptions

if TYPE_CHECKING:
    from app.providers.provider import Provider

import datetime
import logging
import uuid

from pyargon2 import hash
from sqlmodel import Session, SQLModel, create_engine, desc, select

from app.const import CONFIG, MAINTENANCE_MODE

from .exceptions import (
    AccessoryDoesntExist,
    LocationExists,
    ProviderDoesntExist,
    UserDoesNotExist,
    UserExists,
)
from .models import (
    Accessory,
    AccessoryProvider,
    FruityTagRollingAccessoryInfo,
    FruityTagStaticAccessoryInfo,
    Location,
    LocationInfo,
    Permissions,
    User,
)

LOG = logging.getLogger(__name__)


class Database:
    providers: dict[AccessoryProvider, "Provider"]

    def __init__(self) -> None:
        self.providers = dict()
        self.engine = create_engine(CONFIG.db.uri)
        if not MAINTENANCE_MODE:
            SQLModel.metadata.create_all(self.engine)
        else:
            self._dump_schema()

    def _dump_schema(self):
        LOG.debug("Using the following database schema:")
        for table in SQLModel.metadata.sorted_tables:
            LOG.debug(f"  {table.name}:")
            for column in table.columns:
                LOG.debug(f"    {column.name}:")
                LOG.debug(f"      type: {column.type.as_generic}")
                LOG.debug(f"      nullable: {column.nullable}")

    async def _provider_by_accessory(self, accessory: Accessory) -> "Provider | None":
        provider = self.providers.get(accessory.provider, None)
        if not provider:
            LOG.warning(f"Couldn't find an active provider for: {accessory.provider}")
            return None
        return provider

    async def _ensure_admin(self, admin_user_name: str, admin_pwd: str) -> None:
        admin_user = await self.get_user(admin_user_name)
        if not admin_user:
            await self.add_user(
                admin_user_name, admin_pwd, permissions=Permissions.ADMIN
            )
        else:
            await self.update_password(admin_user, admin_pwd)
            admin_user.permissions = Permissions.ADMIN
            await self.update_user(admin_user)

    async def _hash_pwd(self, password: str) -> str:
        return hash(password, CONFIG.jwt.secret)

    async def _location_exists(self, location: Location) -> bool:
        statement = select(Location).where(Location.id == location.id)

        with self.session as session:
            result = session.exec(statement)

            return len(result.all()) > 0

    async def _accessory_exists(self, accessory: Accessory) -> bool:
        statement = select(Accessory).where(Accessory.id == accessory.id)

        with self.session as session:
            result = session.exec(statement)

            return len(result.all()) > 0

    async def setup(self) -> None:
        await self._ensure_admin(CONFIG.admin.name, CONFIG.admin.password)

    async def shutdown(self) -> None:
        pass

    async def location_exists(self, location: Location) -> bool:
        statement = select(type(location)).where(type(location).id == location.id)

        with self.session as session:
            result = session.exec(statement)

            return len(result.all()) > 0

    async def add_location(self, location: Location) -> None:
        if await self._location_exists(location):
            raise LocationExists("Location already exists")

        with self.session as session:
            session.add(location)
            session.commit()

            session.refresh(location)

    async def add_provider(self, type: AccessoryProvider, provider: "Provider") -> None:
        self.providers[type] = provider

    async def get_users(self) -> list[User]:
        statement = select(User)
        with self.session as session:
            result = session.exec(statement)

            return list(result.all())

    async def get_user(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        with self.session as session:
            result = session.exec(statement=statement)

            return result.one_or_none()

    async def get_user_by_id(self, id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == id)
        with self.session as session:
            result = session.exec(statement=statement)

            return result.one_or_none()

    async def get_accessories_by_user(self, user: User) -> list[Accessory]:
        statement = select(Accessory).where(Accessory.user_id == user.id)
        with self.session as session:
            results = session.exec(statement=statement)
            accessories = results.all()
        return list(accessories)

    async def get_accessory_info(
        self, accessory: Accessory
    ) -> Union[FruityTagStaticAccessoryInfo, FruityTagRollingAccessoryInfo, None]:
        provider = self.providers.get(accessory.provider, None)
        if not provider:
            raise UNKNOW_PROVIDER_EXCEPTION

        info = await provider.get_accessory_info(accessory)
        return info

    async def get_accessory_by_id(
        self, user: User, accessory_id: uuid.UUID
    ) -> Accessory:
        statement = select(Accessory).where(
            Accessory.user_id == user.id, Accessory.id == accessory_id
        )
        with self.session as session:
            result = session.exec(statement=statement)
            accessory = result.one_or_none()

        if not accessory:
            raise AccessoryDoesntExist(
                f"Couldn't find accessory with id {accessory_id}"
            )

        return accessory

    async def get_last_location(self, accessory: Accessory) -> Location | None:
        statement = (
            select(Location)
            .where(Location.accessory_id == accessory.id)
            .order_by(desc(Location.timestamp))
            .limit(1)
        )
        with self.session as session:
            result = session.exec(statement=statement)
            return result.one_or_none()

    async def get_location_by_id(
        self, accessory: Accessory, location_id: uuid.UUID
    ) -> Location | None:
        statement = select(Location).where(
            Location.accessory_id == accessory.id, Location.id == location_id
        )
        with self.session as session:
            result = session.exec(statement=statement)
            return result.one_or_none()

    async def get_location_info(
        self, accessory: Accessory, location: Location
    ) -> LocationInfo | None:
        provider = await self._provider_by_accessory(accessory)
        if not provider:
            raise ProviderDoesntExist(
                f"The provider {accessory.provider} is unavailable"
            )
        location_info = await provider.get_location_info(
            accessory=accessory, location=location
        )
        return location_info

    async def get_locations(
        self,
        accessory: Accessory,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        limit: int | None = None,
    ) -> list[Location]:
        statement = (
            select(Location)
            .where(
                Location.accessory_id == accessory.id,
                Location.timestamp >= start_date,
                Location.timestamp <= end_date,
            )
            .order_by(desc(Location.timestamp))
            .limit(limit)
        )
        with self.session as session:
            results = session.exec(statement=statement)
            return list(results.all())

    async def get_provider(self, provider: AccessoryProvider) -> "Provider":
        if instance := self.providers.get(provider, None):
            return instance
        raise ProviderDoesntExist(
            f"The provider is not available at the moment: {provider}"
        )

    async def add_user(
        self, username: str, password: str, permissions: int = Permissions.USER
    ) -> User:
        if await self.get_user(username=username):
            raise UserExists("User already exists")

        new_user = User(
            username=username,
            password_hash=await self._hash_pwd(password=password),
            permissions=permissions,
        )
        with self.session as session:
            session.add(new_user)
            session.commit()

            session.refresh(new_user)
        return new_user

    async def add_accessory(self, accessory: Accessory) -> Accessory:
        with self.session as session:
            session.add(accessory)
            session.commit()
            session.refresh(accessory)
        return accessory

    async def update_user(self, user: User) -> User:
        with self.session as session:
            session.add(user)
            session.commit()

            session.refresh(user)

        return user

    async def update_accessory(self, accessory: Accessory) -> Accessory:
        with self.session as session:
            session.add(accessory)
            session.commit()
            session.refresh(accessory)
        return accessory

    async def update_accessory_info(
        self, accessory: Accessory, accessory_options: AccessoryOptions
    ):
        provider = await self._provider_by_accessory(accessory)
        if not provider:
            raise UNKNOW_PROVIDER_EXCEPTION
        await provider.update_accessory_info(accessory, accessory_options)

    async def update_password(self, user: User, new_password: str) -> User:
        user.password_hash = await self._hash_pwd(new_password)
        with self.session as session:
            session.add(user)
            session.commit()

            session.refresh(user)
        return user

    async def remove_accessory(self, accessory: Accessory) -> None:
        info = await self.get_accessory_info(accessory)
        with self.session as session:
            if info:
                try:
                    session.delete(info)
                except Exception as ex:
                    LOG.warning(f"Couldn't remove accessory info: {ex}")
            try:
                session.delete(accessory)
            except Exception as ex:
                LOG.warning(f"Couldn't remove accessory: {ex}")
            session.commit()

    async def remove_user(self, id: uuid.UUID) -> None:
        user = await self.get_user_by_id(id=id)
        if not user:
            raise UserDoesNotExist("User does not exist")
        with Session(self.engine) as session:
            session.delete(user)
            session.commit()

    async def verify(self, user: User, password: str) -> bool:
        pwd_hash = await self._hash_pwd(password=password)

        return pwd_hash == user.password_hash

    @property
    def session(self) -> Session:
        return Session(self.engine)
