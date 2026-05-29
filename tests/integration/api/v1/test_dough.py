from unicodedata import decimal
import pytest


import app.api.v1.endpoints.dough.crud as dough_crud
from app.api.v1.endpoints.dough.schemas import DoughCreateSchema
from app.database.connection import SessionLocal

@pytest.fixture(scope='module')
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_dough_create_read_delete(db):
            len_dough_before = len(dough_crud.get_all_doughs(db))
            new_dough = DoughCreateSchema(
                name='awesome dough',
                price= 4.99,
                description= 'awesome description',
                stock= 1
            )

            db_dough = dough_crud.create_dough(new_dough,db)
            created_dough_id = db_dough.id
            all_doughs = dough_crud.get_all_doughs(db)
            assert len(all_doughs) == len_dough_before + 1
            read_dough = dough_crud.get_dough_by_id(created_dough_id,db)
            assert read_dough.id == created_dough_id
            assert read_dough.name == 'awesome dough'
            assert read_dough.description == 'awesome description'
            assert read_dough.price == decimal(4.99)
            assert read_dough.stock == 1

            dough_crud.delete_dough_by_id(created_dough_id,db)
            all_doughs = dough_crud.get_all_doughs(db)
            deleted_dough = dough_crud.delete_dough_by_id(created_dough_id,db)
            assert len(all_doughs) == len_dough_before
            assert deleted_dough is None

