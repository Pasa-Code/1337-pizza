import pytest

import app.api.v1.endpoints.order.crud as order_crud
import app.api.v1.endpoints.order.address.crud as address_crud
import app.api.v1.endpoints.user.crud as user_crud
from app.api.v1.endpoints.order.schemas import OrderCreateSchema
from app.api.v1.endpoints.order.address.schemas import AddressCreateSchema
from app.api.v1.endpoints.user.schemas import UserCreateSchema
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

    order_crud.delete_order_by_id(created_order_id, db)
    orders = order_crud.get_all_orders(db)
    deleted_order = order_crud.get_order_by_id(created_order_id, db)
    assert len(orders) == len_order_before
    assert deleted_order is None