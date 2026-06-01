import pytest
from decimal import Decimal
import app.api.v1.endpoints.topping.crud as topping_crud
import app.api.v1.endpoints.topping.schemas as topping_schemas
from app.database.connection import SessionLocal

@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_topping_create_read_delete(db):
    new_topping_name = 'test_topping'
    number_of_toppings_before = len(topping_crud.get_all_toppings(db))

    topping = topping_schemas.ToppingCreateSchema(
        name=new_topping_name,
        price=1.50,
        description='test description',
        stock=10
    )

    db_topping = topping_crud.create_topping(topping, db)
    created_topping_id = db_topping.id

    toppings = topping_crud.get_all_toppings(db)
    assert len(toppings) == number_of_toppings_before + 1

    read_topping = topping_crud.get_topping_by_id(created_topping_id, db)

    assert read_topping.id == created_topping_id
    assert read_topping.name == new_topping_name
    assert read_topping.price == Decimal('1.50')
    assert read_topping.description == 'test description'
    assert read_topping.stock == 10

    topping_crud.delete_topping_by_id(created_topping_id, db)
    toppings = topping_crud.get_all_toppings(db)
    assert len(toppings) == number_of_toppings_before

    deleted_topping = topping_crud.get_topping_by_id(created_topping_id, db)
    assert deleted_topping is None

