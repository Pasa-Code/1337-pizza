# tests/integration/api/v1/test_beverage_crud.py
import pathlib
import subprocess
import uuid
from decimal import Decimal

import pytest

from app.database.connection import SessionLocal

import app.api.v1.endpoints.beverage.crud as beverage_crud
from app.api.v1.endpoints.beverage.schemas import BeverageCreateSchema

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    base_path = pathlib.Path(__file__).resolve()
    project_root = base_path.parents[4]

    print(base_path)
    print("ROOT:", project_root)
    print("INI?", (project_root / "alembic.ini").exists())

    subprocess.run(["alembic", "upgrade", "head"], cwd=project_root, check=True)


    yield


@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_beverage_create_read_delete(db):
    # Anzahl vor dem Anlegen merken
    len_before = len(beverage_crud.get_all_beverages(db))

    new_beverage = BeverageCreateSchema(
        name="Cola Zero",
        price=Decimal("1.99"),
        description="Zuckerfreie Cola",
        stock=5,
    )

    # CREATE
    db_beverage = beverage_crud.create_beverage(new_beverage, db)
    created_id = db_beverage.id

    # READ: alle
    all_beverages = beverage_crud.get_all_beverages(db)
    assert len(all_beverages) == len_before + 1

    # READ: by id
    read_by_id = beverage_crud.get_beverage_by_id(created_id, db)
    assert read_by_id is not None
    assert read_by_id.id == created_id
    assert read_by_id.name == "Cola Zero"
    assert read_by_id.description == "Zuckerfreie Cola"
    assert read_by_id.price == Decimal("1.99")
    assert read_by_id.stock == 5

    # READ: by name
    read_by_name = beverage_crud.get_beverage_by_name("Cola Zero", db)
    assert read_by_name is not None
    assert read_by_name.id == created_id

    # DELETE
    beverage_crud.delete_beverage_by_id(created_id, db)

    all_after_delete = beverage_crud.get_all_beverages(db)
    assert len(all_after_delete) == len_before

    # sollte nach dem löschen nicht gefunden werden
    deleted = beverage_crud.get_beverage_by_id(created_id, db)
    assert deleted is None


def test_beverage_update(db):
    create_schema = BeverageCreateSchema(
        name="Fanta Orange",
        price=Decimal("1.49"),
        description="Orangenlimonade",
        stock=10,
    )
    db_beverage = beverage_crud.create_beverage(create_schema, db)
    beverage_id = db_beverage.id


    update_schema = BeverageCreateSchema(
        name="Fanta Exotic",
        price=Decimal("1.79"),
        description="Exotic Limo",
        stock=7,
    )

    updated = beverage_crud.update_beverage(db_beverage, update_schema, db)

    assert updated.id == beverage_id
    assert updated.name == "Fanta Exotic"
    assert updated.description == "Exotic Limo"
    assert updated.price == Decimal("1.79")
    assert updated.stock == 7


    beverage_crud.delete_beverage_by_id(beverage_id, db)


def test_get_beverage_by_name_not_existing(db):
    result = beverage_crud.get_beverage_by_name("NameDenEsNichtGibt", db)
    assert result is None


def test_delete_beverage_by_id_not_existing(db):
    random_id = uuid.uuid4()

    len_before = len(beverage_crud.get_all_beverages(db))

    beverage_crud.delete_beverage_by_id(random_id, db)

    len_after = len(beverage_crud.get_all_beverages(db))
    assert len_before == len_after
