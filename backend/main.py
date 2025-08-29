import uuid
from contextlib import asynccontextmanager
from typing import Annotated

import jwt
from const import CONFIG
from database.exceptions import AccessoryExists, UserExists
from database.models import Accessory, User
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from FindMy import FindMy
from FindMy.exceptions import NotBase64, WrongColorFormat
from helpers import (
    ACCESSORY_NOT_FOUND_EXCEPTION,
    CREDENTIALS_EXCEPTION,
    USER_NOT_FOUND_EXCEPTION,
    USER_NOT_PERMITTED_EXCEPTION,
    CookieType,
    TokenType,
    create_access_token,
    create_refresh_token,
)
from http_models import (
    AccessoriesResponse,
    AccessoryRequest,
    AccessoryResponse,
    AdvertisementRequest,
    AdvertisementResponse,
    ChangePasswordRequest,
    CreateAccessoryRequest,
    CreateUserRequest,
    LocationRequest,
    LocationResponse,
    LocationsRequest,
    LocationsResponse,
    LoginResponse,
    PrivateKeyResponse,
    RemoveAccessoryRequest,
    RemoveUserRequest,
    UpdateUserRequest,
    UserInfo,
    UsersResponse,
)
from jwt.exceptions import InvalidTokenError

findmy = FindMy()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await findmy.setup()
    yield
    await findmy.shutdown()


app = FastAPI(lifespan=lifespan)
api = FastAPI()

if CONFIG.cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONFIG.cors.cors_origins,
        allow_credentials=CONFIG.cors.allow_credentials,
        allow_methods=CONFIG.cors.cors_methods,
        allow_headers=CONFIG.cors.cors_headers,
    )

app.mount("/api", api)
app.mount("/", StaticFiles(directory=CONFIG.frontend.path, html=True), name="frontend")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(
            jwt=token, key=CONFIG.jwt.secret, algorithms=[CONFIG.jwt.algorithm]
        )

        token_type = payload.get("type", None)
        userid_str = payload.get("userid", None)
        if token_type != TokenType.ACCESS.value or userid_str is None:
            raise CREDENTIALS_EXCEPTION

        userid = uuid.UUID(userid_str)

    except (InvalidTokenError, TypeError) as ex:
        raise CREDENTIALS_EXCEPTION

    user = await findmy.db.get_user_by_id(userid)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@api.post("/login")
async def login(
    response: Response, login_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> LoginResponse:
    user = await findmy.db.get_user(login_data.username)
    if not user or not await findmy.db.verify(user, login_data.password):
        raise USER_NOT_PERMITTED_EXCEPTION

    access_token = create_access_token(
        data={"userid": str(user.id), "is_admin": user.admin, "username": user.username}
    )
    refresh_token = create_refresh_token(data={"userid": str(user.id)})

    response.set_cookie(
        key=CookieType.REFRESH.value,
        value=refresh_token,
    )

    return LoginResponse(access_token=access_token, token_type="bearer")


@api.get("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Response:
    response = JSONResponse(content={"detail": "success"})
    response.delete_cookie(
        key=CookieType.REFRESH.value,
    )
    return response


@api.get("/refresh")
async def refresh(request: Request):
    refresh_token = request.cookies.get(CookieType.REFRESH.value, None)

    if not refresh_token:
        raise CREDENTIALS_EXCEPTION

    try:
        payload = jwt.decode(
            jwt=refresh_token,
            key=CONFIG.jwt.secret_refresh,
            algorithms=[CONFIG.jwt.algorithm],
        )
        token_type = payload.get("type", None)

        userid_str = payload.get("userid", None)
        if token_type != TokenType.REFRESH.value or userid_str is None:
            raise CREDENTIALS_EXCEPTION

        userid = uuid.UUID(userid_str)

    except (InvalidTokenError, TypeError):
        raise CREDENTIALS_EXCEPTION

    user = await findmy.db.get_user_by_id(userid)

    if not user:
        raise CREDENTIALS_EXCEPTION

    access_token = create_access_token(data={"userid": str(user.id)})
    return LoginResponse(access_token=access_token, token_type="bearer")


@api.post("/accessory")
async def get_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    accesory_req: AccessoryRequest,
) -> AccessoryResponse:
    if accessory := await findmy.db.get_accessory(
        user=current_user, name=accesory_req.name
    ):
        return AccessoryResponse(accessory=accessory)

    raise ACCESSORY_NOT_FOUND_EXCEPTION


@api.get("/accessories")
async def get_accessories(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AccessoriesResponse:
    accessories = await findmy.db.get_accessories_by_user(current_user)

    return AccessoriesResponse(accessories=accessories)


@api.post("/create")
async def create_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    create_accessory_req: CreateAccessoryRequest,
) -> Accessory:
    try:
        new_accessory = await findmy.create_accessory(
            user=current_user,
            name=create_accessory_req.name,
            color=create_accessory_req.color,
            icon=create_accessory_req.icon,
            private_key_b64=create_accessory_req.private_key,
        )

    except (WrongColorFormat, NotBase64, AccessoryExists) as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )

    return new_accessory


@api.post("/update")
async def update_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    update_accessory_req: CreateAccessoryRequest,
) -> Accessory:
    try:
        new_accessory = await findmy.update_accessory(
            user=current_user,
            name=update_accessory_req.name,
            color=update_accessory_req.color,
            icon=update_accessory_req.icon,
            private_key_b64=update_accessory_req.private_key,
        )

    except (WrongColorFormat, NotBase64, AccessoryExists) as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )

    return new_accessory


@api.post("/remove")
async def remove_accessory(
    current_user: Annotated[User, Depends(get_current_active_user)],
    remove_accessory_req: RemoveAccessoryRequest,
):
    if not await findmy.remove_accessory(
        user=current_user, name=remove_accessory_req.name
    ):
        raise ACCESSORY_NOT_FOUND_EXCEPTION


@api.post("/locations")
async def get_locations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    locations_req: LocationsRequest,
):
    if accessory := await findmy.db.get_accessory(
        user=current_user, name=locations_req.name
    ):
        return LocationsResponse(
            locations=await findmy.get_locations(
                accessory=accessory,
                start_date=locations_req.start,
                end_date=locations_req.end,
            )
        )

    raise ACCESSORY_NOT_FOUND_EXCEPTION


@api.post("/location")
async def get_location(
    current_user: Annotated[User, Depends(get_current_active_user)],
    locations_req: LocationRequest,
):
    if accessory := await findmy.db.get_accessory(
        user=current_user, name=locations_req.name
    ):
        return LocationResponse(
            location=await findmy.db.get_last_location(accessory=accessory)
        )

    raise ACCESSORY_NOT_FOUND_EXCEPTION


@api.get("/privatekey")
async def create_private_key(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PrivateKeyResponse:
    new_priv_key = await findmy.gen_private_key()

    return PrivateKeyResponse(private_key=new_priv_key.private_key_b64)


@api.post("/advertisement")
async def get_advertise_key(
    current_user: Annotated[User, Depends(get_current_active_user)],
    advertisement_req: AdvertisementRequest,
) -> AdvertisementResponse:
    key_pair = await findmy.get_key_pair_by_name(current_user, advertisement_req.name)
    if not key_pair:
        raise ACCESSORY_NOT_FOUND_EXCEPTION

    return AdvertisementResponse(advertisement_key=key_pair.adv_key_b64)


@api.post("/change_password")
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    change_password_req: ChangePasswordRequest,
):
    if not await findmy.db.verify(current_user, change_password_req.old_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Old password is incorrect"
        )

    await findmy.db.update_password(current_user, change_password_req.new_password)


@api.get("/users")
async def get_users(current_user: Annotated[User, Depends(get_current_active_user)]):
    if not current_user.admin:
        raise USER_NOT_PERMITTED_EXCEPTION

    all_users = await findmy.db.get_users()

    return UsersResponse(
        users=[UserInfo(name=user.username, is_admin=user.admin) for user in all_users]
    )


@api.post("/user/create")
async def create_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    create_user_req: CreateUserRequest,
):
    if not current_user.admin:
        raise USER_NOT_PERMITTED_EXCEPTION

    try:
        await findmy.db.add_user(
            username=create_user_req.name,
            password=create_user_req.password,
            is_admin=create_user_req.is_admin,
        )
    except UserExists as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@api.post("/user/remove")
async def remove_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    remove_user_req: RemoveUserRequest,
):
    if not current_user.admin:
        raise USER_NOT_PERMITTED_EXCEPTION

    if current_user.username == remove_user_req.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can't remove yourself"
        )

    try:
        await findmy.db.remove_user(username=remove_user_req.name)
    except UserExists as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@api.post("/user/update")
async def update_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    update_user_req: UpdateUserRequest,
):
    if not current_user.admin:
        raise USER_NOT_PERMITTED_EXCEPTION

    if current_user.username == update_user_req.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can't update yourself"
        )

    user = await findmy.db.get_user(update_user_req.name)
    if not user:
        raise USER_NOT_FOUND_EXCEPTION

    user = await findmy.db.update_password(user, update_user_req.password)
    if user.admin != update_user_req.is_admin:
        user.admin = update_user_req.is_admin
        await findmy.db.update_user(user)
