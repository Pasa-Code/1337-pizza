import uuid
import logging
from sqlalchemy.orm import Session

import app.api.v1.endpoints.beverage.crud as beverage_crud
from app.database.models import Beverage


def beverage_is_available(beverage_id: uuid.UUID, amount: int, db: Session):
    # Get Beverage
    beverage = beverage_crud.get_beverage_by_id(beverage_id, db)
    # Check if Beverage exists
    if not beverage:
        logging.info('beverage with id:{} does not exist'.format(beverage_id))
        return False #wenn getränk nicht existiert
    if (beverage.stock >= amount):
        logging.info('enough beverage with id:{} ,is available'.format(beverage_id))
        return True
    else:
        logging.info('not enough beverage with id:{}, is available'.format(beverage_id))
        return False





def change_stock_of_beverage(beverage_id: uuid.UUID, change_amount: int, db: Session):
    # Get Beverage
    beverage = db.query(Beverage).filter(Beverage.id == beverage_id).first()

    # Check if Beverage exists and if Stock is not getting smaller than zero
    if beverage and beverage.stock + change_amount >= 0:
        setattr(beverage, 'stock', beverage.stock + change_amount)
        db.commit()
        db.refresh(beverage)
        logging.info('changed stock of beverage with id:{}, by amount:{}'.format(beverage_id,change_amount))
        return True
    logging.warning('couldnt change amount of stock from beverage with id:{}, because amount after change would '
                    'be negative amount'.format(beverage_id))
    return False
