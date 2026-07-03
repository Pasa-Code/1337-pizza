import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from sqlalchemy.orm import Session
import logging

import app.api.v1.endpoints.sauce.crud as sauce_crud
from app.api.v1.endpoints.sauce.schemas import SauceSchema, SauceCreateSchema, SauceListItemSchema
from app.database.connection import SessionLocal
from app.api.v1.constants import NOT_FOUND_ERROR_OUTPUT

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('', response_model=List[SauceListItemSchema], tags=['sauce'])
def get_all_sauces(db: Annotated[Session, Depends(get_db)]):
    return sauce_crud.get_all_sauces(db)


@router.post('', response_model=SauceSchema, status_code=status.HTTP_201_CREATED, tags=['sauce'])
def create_sauce(sauce: SauceCreateSchema,
                 request: Request,
                 db: Annotated[Session, Depends(get_db)],
                 ):
    sauce_found = sauce_crud.get_sauce_by_name(sauce.name, db)
    if sauce_found:
        logging.error('Tried to create a sauce with name {}, but it already exists'.format(sauce.name))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    new_sauce = sauce_crud.create_Sauce(sauce, db)
    return new_sauce


@router.put('/{sauce_id}', response_model=SauceSchema, tags=['sauce'])
def update_sauce(
        sauce_id: uuid.UUID,
        changed_sauce: SauceCreateSchema,
        request: Request,
        response: Response,
        db: Annotated[Session, Depends(get_db)],
):
    sauce_found = sauce_crud.get_sauce_by_id(sauce_id, db)
    update_sauce = None

    if sauce_found:
        if sauce_found.name == changed_sauce.name:
            sauce_crud.update_sauce(sauce_found, changed_sauce, db)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            sauce_name_found = sauce_crud.get_sauce_by_name(changed_sauce.name, db)
            if sauce_name_found:
                logging.error('Sauce {} updated to an already existing name {}'
                              .format(sauce_id, changed_sauce.name))
                raise HTTPException(status_code=status.HTTP_409_CONFLICT)
            else:
                logging.info('Sauce {} updated to a non-existing name {} - creating new Sauce'
                             .format(sauce_id, changed_sauce.name))
                update_sauce = sauce_crud.create_Sauce(changed_sauce, db)
                response.status_code = status.HTTP_201_CREATED
    else:
        logging.error('Tried to update Sauce {}, but it does not exist'.format(sauce_id))
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    return update_sauce


@router.get('/{sauce_id}', response_model=SauceSchema, tags=['sauce'])
def get_sauce(sauce_id: uuid.UUID,
              db: Annotated[Session, Depends(get_db)],
              ):
    sauce = sauce_crud.get_sauce_by_id(sauce_id, db)

    if not sauce:
        logging.error('Tried to get sauce {}, but it does not exist'.format(sauce_id))
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)
    return sauce


@router.delete('/{sauce_id}', response_model=None, tags=['sauce'])
def delete_sauce(sauce_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]):
    sauce = sauce_crud.get_sauce_by_id(sauce_id, db)

    if not sauce:
        logging.error('Tried to delete sauce {}, but it does not exist'.format(sauce_id))
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    sauce_crud.delete_sauce_by_id(sauce_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
