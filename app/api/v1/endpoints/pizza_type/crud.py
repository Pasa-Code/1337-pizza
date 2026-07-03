import uuid
import logging

from sqlalchemy.orm import Session

from app.api.v1.endpoints.pizza_type.schemas import \
    PizzaTypeCreateSchema, \
    PizzaTypeToppingQuantityCreateSchema
from app.database.models import PizzaType, PizzaTypeToppingQuantity, Sauce


def create_pizza_type(schema: PizzaTypeCreateSchema, db: Session):
    #Schauen ob eine Sauce im request angegeben wurde
    if not schema.sauce_id:
        #wenn nicht angegeben in DB nachschauen ob schon eine Tomatensauce existiert
        default_sauce = db.query(Sauce).filter(Sauce.name.ilike('Tomatensauce')).first()
        #fallback: Wenn keine existiert dann eine erstellen
        if not default_sauce:
            default_sauce = Sauce(
                name = 'Tomatensauce',
                price = 0.5,
                description='Klassiker Sauce',
                stock = 10
            )
            db.add(default_sauce)
            db.flush() #Flush, um die id zu erstellen zu lassen während die transaktion nicht zuende ist
            logging.info('Standard-Tomatensauce wurde automatisch in der DB angelegt mit stock = 10.')
        #ID der Tomatensauce dem Schema zuweisen
        schema.sauce_id = default_sauce.id
    entity = PizzaType(**schema.dict())
    db.add(entity)
    db.commit()
    logging.info('Pizza type {} stored in database'.format(entity.name))
    return entity


def get_pizza_type_by_id(pizza_type_id: uuid.UUID, db: Session):
    entity = db.query(PizzaType).filter(PizzaType.id == pizza_type_id).first()
    return entity


def get_pizza_type_by_name(pizza_type_name: str, db: Session):
    entity = db.query(PizzaType).filter(PizzaType.name == pizza_type_name).first()
    return entity


def get_all_pizza_types(db: Session):
    entities = db.query(PizzaType).all()
    return entities


def update_pizza_type(pizza_type: PizzaType, changed_pizza_type: PizzaTypeCreateSchema, db: Session):
    for key, value in changed_pizza_type.dict().items():
        setattr(pizza_type, key, value)

    db.commit()
    db.refresh(pizza_type)
    logging.info('Pizza type {} updated in database'.format(pizza_type.id))

    return pizza_type


def delete_pizza_type_by_id(pizza_type_id: uuid.UUID, db: Session):
    entity = get_pizza_type_by_id(pizza_type_id, db)
    if entity:
        logging.info('Deleting pizza type {} from database'.format(pizza_type_id))
        db.delete(entity)
        db.commit()


def create_topping_quantity(
        pizza_type: PizzaType,
        schema: PizzaTypeToppingQuantityCreateSchema,
        db: Session,
):
    entity = PizzaTypeToppingQuantity(**schema.dict())
    pizza_type.toppings.append(entity)
    db.commit()
    db.refresh(pizza_type)
    logging.info('Added topping {} with quantity {} to pizza type {} in database'
        .format(schema.topping_id,schema.quantity,pizza_type.id))
    return entity


def get_topping_quantity_by_id(
        pizza_type_id: uuid.UUID,
        topping_id: uuid.UUID,
        db: Session,
):
    entity = db.query(PizzaTypeToppingQuantity) \
        .filter(PizzaTypeToppingQuantity.topping_id == topping_id,
                PizzaTypeToppingQuantity.pizza_type_id == pizza_type_id) \
        .first()
    return entity


def get_joined_topping_quantities_by_pizza_type(
        pizza_type_id: uuid.UUID,
        db: Session,
):
    entities = db.query(PizzaTypeToppingQuantity) \
        .filter(PizzaTypeToppingQuantity.pizza_type_id == pizza_type_id)
    return entities.all()
