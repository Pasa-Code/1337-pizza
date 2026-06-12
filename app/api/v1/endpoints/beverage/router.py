import uuid
import logging
from typing import List, Annotated

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from sqlalchemy.orm import Session

import app.api.v1.endpoints.beverage.crud as beverage_crud
from app.api.v1.endpoints.beverage.schemas import BeverageSchema, BeverageCreateSchema, BeverageListItemSchema
from app.database.connection import SessionLocal
from app.api.v1.constants import NOT_FOUND_ERROR_OUTPUT


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get('', response_model=List[BeverageListItemSchema], tags=['beverage'])
def get_all_beverages(db: Annotated[Session, Depends(get_db)]):
    beverages = beverage_crud.get_all_beverages(db)
    return beverages


@router.post('', response_model=BeverageSchema, status_code=status.HTTP_201_CREATED, tags=['beverage'])
def create_beverage(beverage: BeverageCreateSchema,
                    request: Request,
                    db: Annotated[Session, Depends(get_db)]):
    beverage_found = beverage_crud.get_beverage_by_name(beverage.name, db)

    if beverage_found:
        logging.warning(f'Beverage with name {beverage.name} already exists')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    new_beverage = beverage_crud.create_beverage(beverage, db)
    logging.info(f'Created beverage {new_beverage.name}')
    return new_beverage



@router.put('/{beverage_id}', response_model=BeverageSchema, tags=['beverage'])
def update_beverage(
        beverage_id: uuid.UUID,
        changed_beverage: BeverageCreateSchema,
        request: Request,
        response: Response,
        db: Annotated[Session, Depends(get_db)],
):
    beverage_found = beverage_crud.get_beverage_by_id(beverage_id, db)

    if beverage_found:

        if beverage_found.name == changed_beverage.name:
            beverage_crud.update_beverage(beverage_found, changed_beverage, db)

            logging.info(f'Updated beverage {beverage_id}')

            return Response(status_code=status.HTTP_204_NO_CONTENT)

        else:
            beverage_name_found = beverage_crud.get_beverage_by_name(changed_beverage.name, db)

            if beverage_name_found:
                logging.warning(
                    f'Cannot rename beverage {beverage_id} to {changed_beverage.name} because the name already exists'
                )

                raise HTTPException(status_code=status.HTTP_409_CONFLICT)

            else:
                updated_beverage = beverage_crud.create_beverage(changed_beverage, db)

                logging.info(
                    f'Created new beverage {updated_beverage.name} while updating beverage {beverage_id}'
                )

                response.status_code = status.HTTP_201_CREATED

    else:
        logging.error(f'Beverage {beverage_id} not found during update')

        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    return updated_beverage


@router.get('/{beverage_id}', response_model=BeverageSchema, tags=['beverage'])
def get_beverage(
        beverage_id: uuid.UUID,
        db: Annotated[Session, Depends(get_db)],
):
    beverage = beverage_crud.get_beverage_by_id(beverage_id, db)

    if not beverage:
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    return beverage


@router.delete('/{beverage_id}', response_model=None, tags=['beverage'])
def delete_beverage(
        beverage_id: uuid.UUID,
        db: Annotated[Session, Depends(get_db)]):
    beverage = beverage_crud.get_beverage_by_id(beverage_id, db)

    if not beverage:
        logging.error(f'Tried to delete non-existing beverage {beverage_id}')
        raise HTTPException(status_code=404, detail=NOT_FOUND_ERROR_OUTPUT)

    beverage_crud.delete_beverage_by_id(beverage_id, db)
    logging.info(f'Deleted beverage {beverage_id}')
    return Response(status_code=status.HTTP_204_NO_CONTENT)


