import uuid
from typing import List, TypeVar, Annotated

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from sqlalchemy.orm import Session

import app.api.v1.endpoints.dough.crud as dough_crud
import app.api.v1.endpoints.pizza_type.crud as pizza_type_crud
import app.api.v1.endpoints.topping.crud as topping_crud
from app.api.v1.endpoints.dough.schemas import DoughSchema
from app.api.v1.endpoints.pizza_type.schemas import \
    JoinedPizzaTypeQuantitySchema, \
    PizzaTypeSchema, \
    PizzaTypeCreateSchema, \
    PizzaTypeToppingQuantityCreateSchema
from app.database.connection import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('', response_model=List[PizzaTypeSchema], tags=['pizza_type'])
def get_all_pizza_types(db: Annotated[Session, Depends(get_db)]):
    pizza_types = pizza_type_crud.get_all_pizza_types(db)
    return pizza_types


@router.post('', response_model=PizzaTypeSchema, tags=['pizza_type'])
def create_pizza_type(
        pizza_type: PizzaTypeCreateSchema, request: Request,
        response: Response, db: Annotated[Session, Depends(get_db)],
):
    pizza_type_found = pizza_type_crud.get_pizza_type_by_name(pizza_type.name, db)

    if pizza_type_found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    dough = dough_crud.get_dough_by_id(pizza_type.dough_id, db)
    if not dough:
        raise HTTPException(status_code=404, detail='Item not found')

    new_pizza_type = pizza_type_crud.create_pizza_type(pizza_type, db)
    response.status_code = status.HTTP_201_CREATED
    return new_pizza_type


@router.put('/{pizza_type_id}', response_model=PizzaTypeSchema, tags=['pizza_type'])
def update_pizza_type(
        pizza_type_id: uuid.UUID,
        changed_pizza_type: PizzaTypeCreateSchema,
        request: Request,
        response: Response,
        db: Annotated[Session, Depends(get_db)],
):
    pizza_type_found = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)
    updated_pizza_type = None

    if pizza_type_found:
        if pizza_type_found.name == changed_pizza_type.name:
            pizza_type_crud.update_pizza_type(pizza_type_found, changed_pizza_type, db)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            pizza_type_name_found = pizza_type_crud.get_pizza_type_by_name(changed_pizza_type.name, db)
            if pizza_type_name_found:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT)
            else:
                updated_pizza_type = pizza_type_crud.create_pizza_type(changed_pizza_type, db)
                response.status_code = status.HTTP_201_CREATED
    else:
        raise HTTPException(status_code=404, detail='Item not found')

    return updated_pizza_type


@router.get('/{pizza_type_id}', response_model=PizzaTypeSchema, tags=['pizza_type'])
def get_pizza_type(
        pizza_type_id: uuid.UUID,
        db: Annotated[Session, Depends(get_db)],
):
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        raise HTTPException(status_code=404, detail='Item not found')

    return pizza_type


@router.delete('/{pizza_type_id}', response_model=None, tags=['pizza_type'])
def delete_pizza_type(pizza_type_id: uuid.UUID,
                      db: Annotated[Session, Depends(get_db)],
                      ):
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        raise HTTPException(status_code=404, detail='Item not found')

    pizza_type_crud.delete_pizza_type_by_id(pizza_type_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Due to mypy error, this workaround is needed for Union
# see pull request https://github.com/python/mypy/pull/8779
# should be fixed in near future
MyPyEitherItem = TypeVar(
    'MyPyEitherItem',
    List[PizzaTypeToppingQuantityCreateSchema],
    List[JoinedPizzaTypeQuantitySchema],
    None,
)


@router.get(
    '/{pizza_type_id}/toppings',
    response_model=MyPyEitherItem,
    tags=['pizza_type'],
)
def get_pizza_type_toppings(
        pizza_type_id: uuid.UUID,
        response: Response,
        db: Annotated[Session, Depends(get_db)],
        join: bool = False,
):
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        raise HTTPException(status_code=404, detail='Item not found')

    toppings = pizza_type.toppings
    if join:
        toppings = pizza_type_crud.get_joined_topping_quantities_by_pizza_type(pizza_type.id, db)

    return toppings


@router.post(
    '/{pizza_type_id}/toppings',
    response_model=PizzaTypeToppingQuantityCreateSchema,
    status_code=status.HTTP_201_CREATED,
    tags=['pizza_type'],
)
def create_pizza_type_topping(
        pizza_type_id: uuid.UUID,
        topping_quantity: PizzaTypeToppingQuantityCreateSchema,
        request: Request,
        response: Response,
        db: Annotated[Session, Depends(get_db)],
):
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)
    if not pizza_type:
        raise HTTPException(status_code=404, detail='Item not found')

    if not topping_crud.get_topping_by_id(topping_quantity.topping_id, db):
        raise HTTPException(status_code=404, detail='Item not found')

    topping_quantity_found = pizza_type_crud.get_topping_quantity_by_id(pizza_type_id, topping_quantity.topping_id, db)
    if topping_quantity_found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    new_topping_quantity = pizza_type_crud.create_topping_quantity(pizza_type, topping_quantity, db)
    return new_topping_quantity


@router.get(
    '/{pizza_type_id}/dough',
    response_model=DoughSchema,
    tags=['pizza_type'],
)
def get_pizza_type_dough(
        pizza_type_id: uuid.UUID,
        response: Response,
        db: Annotated[Session, Depends(get_db)],
):
    pizza_type = pizza_type_crud.get_pizza_type_by_id(pizza_type_id, db)

    if not pizza_type:
        raise HTTPException(status_code=404, detail='Item not found')

    dough = pizza_type.dough

    return dough
