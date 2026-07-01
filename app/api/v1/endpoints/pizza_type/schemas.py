import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.api.v1.endpoints.topping.schemas import ToppingBaseSchema


class PizzaTypeBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float
    description: str


class PizzaTypeCreateSchema(PizzaTypeBaseSchema):
    dough_id: uuid.UUID
    #sauce_id ist Optional, wenn nichts mitgegeben wird,
    #ist es None und es wird Tomatensauce ausgewählt
    sauce_id:Optional[uuid.UUID] = None


class PizzaTypeSchema(PizzaTypeBaseSchema):
    id: uuid.UUID


class PizzaTypeToppingQuantityBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity: int


class PizzaTypeToppingQuantityCreateSchema(PizzaTypeToppingQuantityBaseSchema):
    topping_id: uuid.UUID


class JoinedPizzaTypeQuantitySchema(PizzaTypeBaseSchema, ToppingBaseSchema):
    pass
