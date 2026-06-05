import uuid
import pytest
from decimal import Decimal

import app.api.v1.endpoints.pizza_type.crud as pizza_type_crud
import app.api.v1.endpoints.dough.crud as dough_crud
import app.api.v1.endpoints.topping.crud as topping_crud
from app.api.v1.endpoints.pizza_type.schemas import (
    PizzaTypeCreateSchema,
    PizzaTypeToppingQuantityCreateSchema,
)
from app.api.v1.endpoints.dough.schemas import DoughCreateSchema
from app.api.v1.endpoints.topping.schemas import ToppingCreateSchema
from app.database.connection import SessionLocal


@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope='module')
def test_dough(db):
    """Erstellt einen Dough-Eintrag als Voraussetzung für PizzaType."""
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


@pytest.fixture(scope='module')
def test_topping(db):
    """Erstellt einen Topping-Eintrag als Voraussetzung für ToppingQuantity."""
    topping = topping_crud.create_topping(
        ToppingCreateSchema(
            name='Test Topping für PizzaType',
            price=Decimal('0.50'),
            description='Topping für Integrationstests',
            stock=200,
        ),
        db,
    )
    yield topping
    topping_crud.delete_topping_by_id(topping.id, db)


def test_pizza_type_create_read_delete(db, test_dough):
    number_of_pizza_types_before = len(pizza_type_crud.get_all_pizza_types(db))

    # Arrange
    pizza_type = PizzaTypeCreateSchema(
        name='Test Margherita',
        price=Decimal('7.99'),
        description='Klassische Margherita',
        dough_id=test_dough.id,
    )

    # Act: erstellen
    db_pizza_type = pizza_type_crud.create_pizza_type(pizza_type, db)
    created_id = db_pizza_type.id

    # Assert: eines mehr in DB
    assert len(pizza_type_crud.get_all_pizza_types(db)) == number_of_pizza_types_before + 1

    # Act: lesen per ID
    read_pizza_type = pizza_type_crud.get_pizza_type_by_id(created_id, db)

    # Assert: korrekt gespeichert
    assert read_pizza_type.id == created_id
    assert read_pizza_type.name == 'Test Margherita'
    assert read_pizza_type.description == 'Klassische Margherita'

    # Act: lesen per Name
    read_by_name = pizza_type_crud.get_pizza_type_by_name('Test Margherita', db)
    assert read_by_name.id == created_id

    # Act: löschen
    pizza_type_crud.delete_pizza_type_by_id(created_id, db)

    # Assert: wieder gleiche Anzahl
    assert len(pizza_type_crud.get_all_pizza_types(db)) == number_of_pizza_types_before

    # Assert: wirklich gelöscht
    assert pizza_type_crud.get_pizza_type_by_id(created_id, db) is None


def test_pizza_type_update(db, test_dough):
    # Arrange
    pizza_type = pizza_type_crud.create_pizza_type(
        PizzaTypeCreateSchema(
            name='Test Salami Alt',
            price=Decimal('8.99'),
            description='Alte Beschreibung',
            dough_id=test_dough.id,
        ),
        db,
    )

    # Act: updaten
    updated = pizza_type_crud.update_pizza_type(
        pizza_type,
        PizzaTypeCreateSchema(
            name='Test Salami Neu',
            price=Decimal('9.99'),
            description='Neue Beschreibung',
            dough_id=test_dough.id,
        ),
        db,
    )

    # Assert: Änderungen gespeichert
    assert updated.name == 'Test Salami Neu'
    assert updated.price == Decimal('9.99')
    assert updated.description == 'Neue Beschreibung'

    # Cleanup
    pizza_type_crud.delete_pizza_type_by_id(pizza_type.id, db)


def test_pizza_type_topping_quantity(db, test_dough, test_topping):
    # Arrange: PizzaType erstellen
    pizza_type = pizza_type_crud.create_pizza_type(
        PizzaTypeCreateSchema(
            name='Test Pizza mit Topping',
            price=Decimal('10.99'),
            description='Pizza mit Topping-Test',
            dough_id=test_dough.id,
        ),
        db,
    )

    # Act: Topping hinzufügen
    topping_quantity = pizza_type_crud.create_topping_quantity(
        pizza_type,
        PizzaTypeToppingQuantityCreateSchema(
            quantity=3,
            topping_id=test_topping.id,
        ),
        db,
    )

    # Assert: Topping korrekt gespeichert
    assert topping_quantity.quantity == 3
    assert topping_quantity.topping_id == test_topping.id

    # Act: Topping per ID lesen
    read_topping_qty = pizza_type_crud.get_topping_quantity_by_id(
        pizza_type.id,
        test_topping.id,
        db,
    )
    assert read_topping_qty is not None
    assert read_topping_qty.quantity == 3

    # Act: alle Toppings des PizzaTypes lesen
    all_toppings = pizza_type_crud.get_joined_topping_quantities_by_pizza_type(
        pizza_type.id,
        db,
    )
    assert len(all_toppings) == 1

    # Cleanup
    pizza_type_crud.delete_pizza_type_by_id(pizza_type.id, db)