import uuid

from pydantic import BaseModel, ConfigDict


class SauceBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float
    description: str


class SauceCreateSchema(SauceBaseSchema):
    stock: int


class SauceSchema(SauceCreateSchema):
    id: uuid.UUID


class SauceListItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    price: float
    description: str
