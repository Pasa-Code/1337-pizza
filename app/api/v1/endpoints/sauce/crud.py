import uuid
import logging

from sqlalchemy.orm import Session

from app.api.v1.endpoints.sauce.schemas import SauceCreateSchema
from app.database.models import Sauce

def create_Sauce(schema: SauceCreateSchema, db: Session):
    entity = Sauce(**schema.dict())
    db.add(entity)
    db.commit()
    logging.info('Sauce created with name {}'.format(entity.name))
    return entity


def get_sauce_by_id(sauce_id: uuid.UUID, db: Session):
    entity = db.query(Sauce).filter(Sauce.id == sauce_id).first()
    return entity


def get_sauce_by_name(sauce_name: str, db: Session):
    entity = db.query(Sauce).filter(Sauce.name == sauce_name).first()
    return entity


def get_all_sauces(db: Session):
    return db.query(Sauce).all()


def update_sauce(Sauce: Sauce, changed_sauce: SauceCreateSchema, db: Session):
    for key, value in changed_sauce.dict().items():
        setattr(Sauce, key, value)

    db.commit()
    db.refresh(Sauce)
    logging.info('Sauce {} updated with values name:{}, price:{}, stock:{}, description:{}'
                 .format(Sauce.id,
                         changed_sauce.name,
                         changed_sauce.price,
                         changed_sauce.stock,
                         changed_sauce.description))
    return Sauce


def delete_sauce_by_id(sauce_id: uuid.UUID, db: Session):
    entity = get_sauce_by_id(sauce_id, db)
    if entity:
        db.delete(entity)
        db.commit()
        logging.info('Sauce with id {} has been deleted'.format(entity.id))