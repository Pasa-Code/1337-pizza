import uuid
from decimal import Decimal

import pytest

from app.database.connection import SessionLocal
from app.database.models import PizzaType,Dough,Topping,PizzaTypeToppingQuantity,Sauce
from app.api.v1.endpoints.order.stock_logic.stock_ingredients_crud import (
    ingredients_are_available,
    reduce_stock_of_ingredients,
increase_stock_of_ingredients
)

#unique_name ist dafür da das sich die namen nicht überscheiden damit jeder name unique ist.
# Grund: Test schlug fehl weil die namen schon existierten.
@pytest.fixture(scope='module')
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
#hiilfsfunktion damit sich dieser teil nicht immer wiederholt
def create_pizza_type_with_toppings(db: SessionLocal, dough_stock: int, topping_stock: int, sauce_stock: int,
                                    qty: int) -> PizzaType:
    dough = Dough(
        id=uuid.uuid4(),
        name=f'Test Dough {uuid.uuid4()}',
        price=Decimal('3.50'),
        description='test dough',
        stock=dough_stock,
    )
    topping = Topping(
        id=uuid.uuid4(),
        name=f'Test Topping {uuid.uuid4()}',
        price=Decimal('0.50'),
        description='test topping',
        stock=topping_stock,
    )
    sauce = Sauce(
        id=uuid.uuid4(),
        name=f'Test sauce{uuid.uuid4()}',
        price=Decimal('2.00'),
        description='test sauce',
        stock=sauce_stock
    )
    pizza_type = PizzaType(
        id=uuid.uuid4(),
        name=f'Test Pizza {uuid.uuid4()}',
        price=Decimal('8.99'),
        description='test pizza',
        dough_id=dough.id,
        sauce_id = sauce.id
    )
    db.add_all([dough, topping, pizza_type,sauce])
    db.commit()
    db.refresh(dough)
    db.refresh(topping)
    db.refresh(pizza_type)

    topping_qty = PizzaTypeToppingQuantity(
        pizza_type_id=pizza_type.id,
        topping_id=topping.id,
        quantity=qty,
    )
    db.add(topping_qty)
    db.commit()
    db.refresh(topping_qty)


    pizza_type.dough = dough
    pizza_type.toppings = [topping_qty]

    return pizza_type

def test_ingredients_are_available_true(db):
    pizza_type = create_pizza_type_with_toppings(
        db=db,
        dough_stock=5,
        topping_stock=10,
        sauce_stock=5,
        qty=3,
    )

    assert ingredients_are_available(pizza_type) is True

def test_ingredients_are_available_false_dough_out_of_stock(db):
    pizza_type = create_pizza_type_with_toppings(
        db=db,
        dough_stock=0,   # kein Teig auf Lager
        sauce_stock=5,
        topping_stock=10,
        qty=3,
    )

    assert ingredients_are_available(pizza_type) is False


def test_ingredients_are_available_false_topping_not_enough(db):
    pizza_type = create_pizza_type_with_toppings(
        db=db,
        dough_stock=5,
        sauce_stock= 5,
        topping_stock=2,  # zu wenig toppings
        qty=3,   #benötigte anzahl an toppings
    )
    assert ingredients_are_available(pizza_type) is False

def test_ingredients_are_available_false_sauce_not_enough(db):
    pizza_type = create_pizza_type_with_toppings(
        db = db,
        dough_stock=5,
        sauce_stock=0,
        topping_stock=10,
        qty=2,
    )

def test_reduce_stock_of_ingredients(db):
    pizza_type = create_pizza_type_with_toppings(
        db=db,
        dough_stock=5,
        sauce_stock=5,
        topping_stock=10,
        qty=2,
    )

    old_dough_stock = pizza_type.dough.stock
    old_topping_stock = pizza_type.toppings[0].topping.stock
    old_sauce_stock = pizza_type.sauce.stock

    reduce_stock_of_ingredients(pizza_type, db)
    db.refresh(pizza_type.dough)
    db.refresh(pizza_type.toppings[0].topping)
    db.refresh(pizza_type.sauce)

    assert pizza_type.dough.stock == old_dough_stock - 1
    assert pizza_type.toppings[0].topping.stock == old_topping_stock - 2
    assert pizza_type.sauce.stock == old_sauce_stock - 1

def test_increase_stock_of_ingredients(db):
    pizza_type = create_pizza_type_with_toppings(
        db=db,
        dough_stock=1,
        sauce_stock=1,
        topping_stock=3,
        qty=1,
    )

    old_dough_stock = pizza_type.dough.stock
    old_topping_stock = pizza_type.toppings[0].topping.stock
    old_sauce_stock = pizza_type.sauce.stock

    reduce_stock_of_ingredients(pizza_type, db)
    db.refresh(pizza_type.dough)
    db.refresh(pizza_type.toppings[0].topping)
    db.refresh(pizza_type.sauce)


    increase_stock_of_ingredients(pizza_type, db)
    db.refresh(pizza_type.dough)
    db.refresh(pizza_type.toppings[0].topping)
    db.refresh(pizza_type.sauce)

    assert pizza_type.dough.stock == old_dough_stock
    assert pizza_type.toppings[0].topping.stock == old_topping_stock
    assert pizza_type.sauce.stock == old_sauce_stock