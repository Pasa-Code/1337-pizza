from decimal import Decimal
import pytest

import app.api.v1.endpoints.beverage.crud as beverage_crud
from app.api.v1.endpoints.beverage.schemas import BeverageCreateSchema
from app.database.connection import SessionLocal


@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_beverage_create_read_delete(db):
    len_beverage_before = len(beverage_crud.get_all_beverages(db))

    new_beverage = BeverageCreateSchema(
        name='Cognac',
        price=3.99,
        description='A sweet and strongly alcoholic drink, twice distilled and left to mature for several years. Classy as fornication.',
        stock=1
    )

    db_beverage = beverage_crud.create_beverage(new_beverage, db)
    created_beverage_id = db_beverage.id

    beverages = beverage_crud.get_all_beverages(db)
    assert len(beverages) == len_beverage_before + 1

    read_beverage = beverage_crud.get_beverage_by_id(created_beverage_id, db)
    assert read_beverage.id == created_beverage_id
    assert read_beverage.name == new_beverage.name
    assert read_beverage.description == new_beverage.description
    assert read_beverage.price == Decimal('3.99')
    assert read_beverage.stock == new_beverage.stock

    beverage_crud.delete_beverage_by_id(created_beverage_id, db)
    beverages = beverage_crud.get_all_beverages(db)
    deleted_beverage = beverage_crud.get_beverage_by_id(created_beverage_id, db)
    assert len(beverages) == len_beverage_before
    assert deleted_beverage is None