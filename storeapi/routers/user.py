import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from storeapi import tasks
from storeapi.database import database, user_table
from storeapi.models.users import UserIn
from storeapi.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="A user with tha email already exists"
        )

    query = user_table.insert().values(email=user.email, password=get_password_hash(user.password))
    logger.debug(query)
    await database.execute(query)
    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    )

    return {"detail": "User created. Please confirm your email"}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = user_table.update().where(user_table.c.email == email).values(confirmed=True)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User confirmed"}
