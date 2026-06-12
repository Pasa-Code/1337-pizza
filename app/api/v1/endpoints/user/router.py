import logging
import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import Response

import app.api.v1.endpoints.user.crud as user_crud
from app.api.v1.endpoints.user.schemas import UserSchema, UserCreateSchema
from app.database.connection import SessionLocal
from app.api.v1.constants import NOT_FOUND_ERROR_OUTPUT

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('', response_model=List[UserSchema], tags=['user'])
def get_all_users(
        db: Annotated[Session, Depends(get_db)],
):
    users = user_crud.get_all_users(db)
    return users


@router.post('', response_model=UserSchema, status_code=status.HTTP_201_CREATED, tags=['user'])
def create_user(user: UserCreateSchema, db: Annotated[Session, Depends(get_db)]):
    logging.info('POST user endpoint called for username {}'.format(user.username))
    new_user = user_crud.create_user(user, db)
    return new_user


@router.put('/{user_id}', response_model=None, tags=['user'])
def update_user(
        user_id: uuid.UUID,
        changed_user: UserCreateSchema,
        db: Annotated[Session, Depends(get_db)],
):
    logging.info('PUT user endpoint called for user id {}'.format(user_id))

    user_found = user_crud.get_user_by_id(user_id, db)

    if user_found:
        user_crud.update_user(user_found, changed_user, db)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        logging.warning('Cannot update user with id {} because user was not found'.format(user_id))
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)


@router.get('/{user_id}', response_model=UserSchema, tags=['user'])
def get_user(user_id: uuid.UUID,
             response: Response,
             db: Annotated[Session, Depends(get_db)]):
    user_found = user_crud.get_user_by_id(user_id, db)

    if not user_found:
        logging.warning('Cannot get user with id {} because user was not found'.format(user_id))
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    logging.info('GET user endpoint returned user with id {}'.format(user_id))
    return user_found


@router.delete('/{user_id}', response_model=None, tags=['user'])
def delete_user(
        user_id: uuid.UUID,
        db: Annotated[Session, Depends(get_db)],
):
    logging.info('DELETE user endpoint called for user id {}'.format(user_id))

    user_found = user_crud.get_user_by_id(user_id, db)

    if not user_found:
        logging.warning('Cannot delete user with id {} because user was not found'.format(user_id))
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    user_crud.delete_user_by_id(user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
