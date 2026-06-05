import uuid
from decimal import Decimal

import pytest

from app.database.connection import SessionLocal
from app.database.models import Beverage
from app.api.v1.endpoints.order.stock_logic.stock_beverage_crud import (
    beverage_is_available,
    change_stock_of_beverage,
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


def test_beverage_is_available_true(db):
    unique_name = f'Available Drink {uuid.uuid4()}'
    bev = Beverage(
        id=uuid.uuid4(),
        name=unique_name,
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
    unique_name = f'Low Stock Drink {uuid.uuid4()}'
    bev = Beverage(
        id=uuid.uuid4(),
        name=unique_name,
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
    expected_stock = 8
    unique_name = f'Increase Stock {uuid.uuid4()}'
    bev = Beverage(
        id=uuid.uuid4(),
        name=unique_name,
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
    assert bev.stock == expected_stock


def test_change_stock_of_beverage_decrease_to_zero(db):
    unique_name = f'Decrease To Zero {uuid.uuid4()}'
    bev = Beverage(
        id=uuid.uuid4(),
        name=unique_name,
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
    expected_stock = 2
    unique_name = f'Prevent Negative {uuid.uuid4()}'
    bev = Beverage(
        id=uuid.uuid4(),
        name=unique_name,
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
    assert bev.stock == expected_stock


def test_change_stock_of_beverage_not_existing(db):
    random_id = uuid.uuid4()

    ok = change_stock_of_beverage(random_id, change_amount=5, db=db)

    assert ok is False
