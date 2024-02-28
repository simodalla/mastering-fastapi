import logging

from fastapi import APIRouter, HTTPException, status

from storeapi.database import database, user_table
from storeapi.models.users import UserIn
from storeapi.security import get_password_hash, get_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="A user with tha email already exists"
        )

    query = user_table.insert().values(email=user.email, password=get_password_hash(user.password))
    logger.debug(query)
    await database.execute(query)

    return {"detail": "User created."}