import pytest
from decimal import Decimal

import app.api.v1.endpoints.order.crud as order_crud
import app.api.v1.endpoints.order.address.crud as address_crud
import app.api.v1.endpoints.user.crud as user_crud
import app.api.v1.endpoints.pizza_type.crud as pizzatype_crud
import app.api.v1.endpoints.dough.crud as dough_crud
import app.api.v1.endpoints.beverage.crud as beverage_crud
from app.api.v1.endpoints.order.schemas import OrderCreateSchema, OrderBeverageQuantityCreateSchema
from app.api.v1.endpoints.order.address.schemas import AddressCreateSchema
from app.api.v1.endpoints.user.schemas import UserCreateSchema
from app.api.v1.endpoints.pizza_type.schemas import PizzaTypeCreateSchema
from app.api.v1.endpoints.dough.schemas import DoughCreateSchema
from app.api.v1.endpoints.beverage.schemas import BeverageCreateSchema
from app.database.models import OrderStatus
from app.database.connection import SessionLocal

@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_order_create_read_delete(db):
    len_order_before = len(order_crud.get_all_orders(db))
    len_addresses_before = len(address_crud.get_all_addresses(db))

    new_address = AddressCreateSchema(
        street='Pizza Street',
        post_code='123456',
        house_number=1,
        country='Pizza Land',
        town='Pizza Town',
        first_name='John',
        last_name='Pizza'
    )
    db_address = address_crud.create_address(new_address, db)
    address_id = db_address.id

    read_address = address_crud.get_address_by_id(address_id, db)
    assert read_address.street == new_address.street
    assert read_address.post_code == new_address.post_code
    assert read_address.house_number == new_address.house_number
    assert read_address.country == new_address.country
    assert read_address.town == new_address.town
    assert read_address.first_name == new_address.first_name
    assert read_address.last_name == new_address.last_name

    new_user = UserCreateSchema(
        username='john-pizza1337'
    )
    db_user = user_crud.create_user(new_user, db)
    user_id = db_user.id

    addresses = address_crud.get_all_addresses(db)
    assert len(addresses) == len_addresses_before + 1

    new_order = OrderCreateSchema(
        address=new_address,
        user_id=user_id,
    )

    db_order = order_crud.create_order(new_order, db)
    created_order_id = db_order.id

    orders = order_crud.get_all_orders(db)
    assert len(orders) == len_order_before + 1

    read_order = order_crud.get_order_by_id(created_order_id, db)
    assert read_order.id == created_order_id
    assert read_order.user_id == new_order.user_id

    order_crud.update_order_status(db_order, OrderStatus.COMPLETED, db)
    read_order = order_crud.get_order_by_id(created_order_id, db)
    assert read_order.order_status == OrderStatus.COMPLETED

    new_dough = DoughCreateSchema(
        name='Dough',
        price=5,
        description='Description',
        stock=1
    )
    db_dough = dough_crud.create_dough(new_dough, db)
    created_dough_id = db_dough.id
    new_pizzatype = PizzaTypeCreateSchema(
        name='Pizza',
        price=10,
        description='Description',
        dough_id=created_dough_id
    )
    db_pizzatype = pizzatype_crud.create_pizza_type(new_pizzatype, db)
    created_pizza = order_crud.add_pizza_to_order(db_order, db_pizzatype, db)
    created_pizza_id = created_pizza.id
    assert len(order_crud.get_all_pizzas_of_order(db_order, db)) == 1

    pizza_price = order_crud.get_price_of_pizza_in_order(created_order_id, db)
    assert pizza_price == Decimal('10')

    order_crud.delete_pizza_from_order(db_order, created_pizza_id, db)
    read_pizza = order_crud.get_pizza_by_id(created_pizza_id, db)
    assert read_pizza is None

    order_crud.delete_order_by_id(created_order_id, db)
    orders = order_crud.get_all_orders(db)
    deleted_order = order_crud.get_order_by_id(created_order_id, db)
    assert len(orders) == len_order_before
    assert deleted_order is None

def test_order_beverage_quantities(db):
    new_address = AddressCreateSchema(
        street='abc',
        post_code='133787',
        house_number=3,
        country='def',
        town='ghi',
        first_name='eee',
        last_name='bbb'
    )
    address_crud.create_address(new_address, db)

    new_user = UserCreateSchema(
        username='testuser'
    )
    db_user = user_crud.create_user(new_user, db)
    user_id = db_user.id
    new_order = OrderCreateSchema(
        address=new_address,
        user_id=user_id,
    )

    db_order = order_crud.create_order(new_order, db)
    created_order_id = db_order.id

    new_beverage = BeverageCreateSchema(
        name='Beer',
        price=5,
        description='i drank a beer',
        stock=10
    )
    db_beverage = beverage_crud.create_beverage(new_beverage, db)
    created_beverage_id = db_beverage.id
    new_beverage_quantity = OrderBeverageQuantityCreateSchema(
        beverage_id=created_beverage_id,
        quantity=10
    )
    order_crud.create_beverage_quantity(db_order, new_beverage_quantity, db)
    read_beverage_quantity = order_crud.get_beverage_quantity_by_id(created_order_id, created_beverage_id, db)
    assert read_beverage_quantity.beverage_id == created_beverage_id
    assert read_beverage_quantity.quantity == new_beverage_quantity.quantity
    order_crud.update_beverage_quantity_of_order(created_order_id, created_beverage_id,
                                                 2 * new_beverage_quantity.quantity,
                                                 db)
    read_beverage_quantity = order_crud.get_beverage_quantity_by_id(created_order_id, created_beverage_id, db)
    assert read_beverage_quantity.quantity == 2 * new_beverage_quantity.quantity

    beverage_price = order_crud.get_price_of_beverage_in_order(created_order_id, db)
    pizza_price = order_crud.get_price_of_pizza_in_order(created_order_id, db)
    order_price = order_crud.get_price_of_order(created_order_id, db)
    assert beverage_price == Decimal('100')
    assert pizza_price is None
    assert order_price == Decimal('100')