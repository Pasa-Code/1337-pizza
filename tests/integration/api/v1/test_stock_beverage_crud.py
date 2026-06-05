# tests/integration/api/v1/test_stock_beverage_logic.py

import uuid
from decimal import Decimal

import pytest

from app.database.connection import SessionLocal
from app.database.models import Beverage
from app.api.v1.endpoints.order.stock_logic.stock_beverage_crud import (
    beverage_is_available,
    change_stock_of_beverage,
)


@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_beverage_is_available_true(db):
    bev = Beverage(
        id=uuid.uuid4(),
        name='Available Drink',
        price=Decimal('1.99'),
        description='enough stock',
        stock=10,
    )
    db.add(bev)
    db.commit()
    db.refresh(bev)

    result = beverage_is_available(bev.id, amount=5, db=db)

    assert result is True


def test_beverage_is_available_false_not_enough_stock(db):
    bev = Beverage(
        id=uuid.uuid4(),
        name='Low Stock Drink',
        price=Decimal('0.99'),
        description='low stock',
        stock=2,
    )
    db.add(bev)
    db.commit()
    db.refresh(bev)

    result = beverage_is_available(bev.id, amount=5, db=db)

    assert result is False


def test_beverage_is_available_false_not_existing(db):
    random_id = uuid.uuid4()

    result = beverage_is_available(random_id, amount=1, db=db)

    assert result is False


def test_change_stock_of_beverage_increase(db):
    bev = Beverage(
        id=uuid.uuid4(),
        name='Increase Stock',
        price=Decimal('2.49'),
        description='increase',
        stock=5,
    )
    db.add(bev)
    db.commit()
    db.refresh(bev)

    ok = change_stock_of_beverage(bev.id, change_amount=3, db=db)
    db.refresh(bev)

    assert ok is True
    assert bev.stock == 8


def test_change_stock_of_beverage_decrease_to_zero(db):
    bev = Beverage(
        id=uuid.uuid4(),
        name='Decrease To Zero',
        price=Decimal('1.50'),
        description='dec to zero',
        stock=3,
    )
    db.add(bev)
    db.commit()
    db.refresh(bev)

    ok = change_stock_of_beverage(bev.id, change_amount=-3, db=db)
    db.refresh(bev)

    assert ok is True
    assert bev.stock == 0


def test_change_stock_of_beverage_prevent_negative(db):
    bev = Beverage(
        id=uuid.uuid4(),
        name='Prevent Negative',
        price=Decimal('1.20'),
        description='neg',
        stock=2,
    )
    db.add(bev)
    db.commit()
    db.refresh(bev)

    ok = change_stock_of_beverage(bev.id, change_amount=-3, db=db)
    db.refresh(bev)

    assert ok is False
    assert bev.stock == 2


def test_change_stock_of_beverage_not_existing(db):
    random_id = uuid.uuid4()

    ok = change_stock_of_beverage(random_id, change_amount=5, db=db)

    assert ok is False
