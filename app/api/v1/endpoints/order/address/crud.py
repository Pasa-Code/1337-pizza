import uuid
import logging
from sqlalchemy.orm import Session

from app.api.v1.endpoints.order.address.schemas import AddressCreateSchema
from app.database.models import Address


def create_address(schema: AddressCreateSchema, db: Session):
    entity = Address(**schema.dict())

    db.add(entity)
    db.commit()
    logging.info('Following address {} was added. Street:{},house number:{}, post code:{}, town:{},country:{}'
                 .format(entity.id,entity.street,
    entity.house_number,
    entity.post_code,
    entity.town,
    entity.country))
    return entity


def get_address_by_id(address_id: uuid.UUID, db: Session):
    entity = db.query(Address).filter(Address.id == address_id).first()
    if entity:
        logging.info('Address with id was returned {}'.format(entity.id))
    else:
        logging.warning('Address with id:{} was not found'.format(address_id))
    return entity


def delete_address_by_id(address_id: uuid.UUID, db: Session):
    entity = get_address_by_id(address_id,db)
    if entity:
        db.delete(entity)
        db.commit()
        logging.info('Address with id was deleted: {}'.format(entity.id))


def update_address(address: Address, changed_address: AddressCreateSchema, db: Session):
    for key, value in changed_address.dict().items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)
    logging.info('Address with following id was updated {}'.format(address.id))
    return address


def get_all_addresses(db: Session):
    logging.info('Getting all addresses')
    return db.query(Address).all()
