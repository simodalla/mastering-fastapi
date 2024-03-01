import logging

from fastapi import APIRouter, HTTPException, Request

from storeapi.database import comment_table, database, post_table
from storeapi.models.posts import Comment, CommentIn, UserPost, UserPostIn, UserPostWithComments
from storeapi.models.users import User
from storeapi.security import get_current_user, oauth2_schema

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")

    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)

    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn, request: Request):
    logger.info("Creating post")
    current_user: User = await get_current_user(await oauth2_schema(request))  # noqa

    data = post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    logger.debug(query)

    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")

    query = post_table.select()
    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn, request: Request):
    logger.info("Creating comment")
    current_user: User = await get_current_user(await oauth2_schema(request))  # noqa

    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    data = comment.model_dump()
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    logger.debug(query)

    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info("Getting comments on post")

    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)

    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comment(post_id: int):
    logger.info("Getting post with comments")

    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
