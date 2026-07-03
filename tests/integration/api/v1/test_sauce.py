from decimal import Decimal
import pytest

import app.api.v1.endpoints.dough.crud as dough_crud
from app.api.v1.endpoints.dough.crud import DoughCreateSchema
import app.api.v1.endpoints.sauce.crud as sauce_crud
from app.api.v1.endpoints.sauce.schemas import SauceCreateSchema
import app.api.v1.endpoints.pizza_type.crud as pizza_type_crud
from app.api.v1.endpoints.pizza_type.crud import PizzaTypeCreateSchema
from app.database.connection import SessionLocal

@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_sauce_create_read_delete(db):
            len_sauce_before = len(sauce_crud.get_all_sauces(db))
            new_sauce = SauceCreateSchema(
                name='awesome sauce',
                price= 4.99,
                description= 'awesome description',
                stock= 1
            )

            db_sauce = sauce_crud.create_Sauce(new_sauce,db)
            created_sauce_id = db_sauce.id
            all_sauce = sauce_crud.get_all_sauces(db)
            assert len(all_sauce) == len_sauce_before + 1
            read_sauce = sauce_crud.get_sauce_by_id(created_sauce_id,db)
            assert read_sauce.id == created_sauce_id
            assert read_sauce.name == 'awesome sauce'
            assert read_sauce.description == 'awesome description'
            assert read_sauce.price == Decimal('4.99')
            assert read_sauce.stock == 1

            sauce_crud.delete_sauce_by_id(created_sauce_id,db)
            all_sauce_after_delete = sauce_crud.get_all_sauces(db)
            assert len(all_sauce_after_delete) == len_sauce_before
            deleted_sauce = sauce_crud.get_sauce_by_id(created_sauce_id,db)
            assert deleted_sauce is None


@pytest.fixture
def setup_dough(db):
    dough = dough_crud.create_dough(
        DoughCreateSchema(
            name='Test Teig für PizzaType',
            price=Decimal('1.00'),
            description='Teig für Integrationstests',
            stock=100,
        ),
        db,
    )
    yield dough
    dough_crud.delete_dough_by_id(dough.id, db)


def test_create_default_sauce_via_create_pizza_type(setup_dough,db):
    pizza_type = PizzaTypeCreateSchema(
        name='Test Margherita',
        price=Decimal('7.99'),
        description='Klassische Margherita',
        dough_id=setup_dough.id,
    )
    created_pizza_type = pizza_type_crud.create_pizza_type(pizza_type,db)
    sauce_id_to_delete = created_pizza_type.sauce_id

    try:
        assert created_pizza_type is not None
        assert created_pizza_type.name == 'Test Margherita'

        assert created_pizza_type.sauce_id is not None

        sauce_in_db = sauce_crud.get_sauce_by_id(created_pizza_type.sauce_id,db)
        assert sauce_in_db is not None
        assert sauce_in_db.name == 'Tomatensauce'
    finally:
        pizza_type_crud.delete_pizza_type_by_id(created_pizza_type.id,db)
        sauce_crud.delete_sauce_by_id(sauce_id_to_delete,db)





