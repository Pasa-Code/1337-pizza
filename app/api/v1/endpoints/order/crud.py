import logging
import uuid
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.endpoints.order.address.crud import create_address
from app.api.v1.endpoints.order.schemas import \
    JoinedPizzaPizzaTypeSchema, OrderBeverageQuantityCreateSchema, OrderCreateSchema
from app.database.models import Order, Pizza, PizzaType, OrderBeverageQuantity, Beverage, OrderStatus


def create_order(schema: OrderCreateSchema, db: Session):
    address = create_address(schema.address, db)
    order = Order(user_id=schema.user_id)
    order.address = address
    order.order_status = OrderStatus.TRANSMITTED
    db.add(order)
    db.commit()
    db.refresh(order)   #neu laden bevor wir auf das Feld zugreifen
    logging.info('Created Order with id:{}'.format(order.id))
    return order


def get_order_by_id(order_id: uuid.UUID, db: Session):
    entity = db.query(Order).filter(Order.id == order_id).first()
    if entity:
        logging.info('Order with id:{} was returned'.format(order_id))
    else:
        logging.warning('Order with id:{} does not exist to be returned'.format(order_id))
    return entity


def get_all_orders(db: Session):
    entities = (db.query(Order).order_by(Order.order_datetime.asc())
                .all())
    logging.info('All orders returned')
    return entities

def get_orders_by_status(db: Session, order_status: OrderStatus): # sorted oldest first
    entities = (
        db.query(Order)
        .filter(Order.order_status == order_status)
        .order_by(Order.order_datetime.asc())
        .all()
    )
    logging.info('Orders with status:{} returned'.format(order_status))
    return entities

def delete_order_by_id(order_id: uuid.UUID, db: Session):
    entity = get_order_by_id(order_id, db)
    if entity:
        db.delete(entity)
        db.commit()
        logging.info('Order with id:{} was deleted'.format(order_id))
    else:
        logging.warning('Order with id:{} does not exist to be deleted'.format(order_id))


def update_order_status(order: Order, changed_order: OrderStatus, db: Session):
    setattr(order, 'order_status', changed_order)

    db.commit()
    db.refresh(order)
    logging.info('Order with id:{} was updated to status:{}'.format(order.id,order.order_status))
    return order


def create_pizza(pizza_type: PizzaType,
                 db: Session):
    entity = Pizza()
    if pizza_type:
        entity.pizza_type_id = pizza_type.id
    db.add(entity)
    db.commit()
    logging.info('Created Pizza with id:{},type:{}'.format(entity.id, pizza_type.name))
    return entity


def add_pizza_to_order(order: Order, pizza_type: PizzaType,
                       db: Session):
    pizza = create_pizza(pizza_type, db)
    order.pizzas.append(pizza)
    db.commit()
    db.refresh(order)
    logging.info('added Pizza to order id:{},with pizza type:{}'.format(order.id, pizza_type.name))
    return pizza


def get_pizza_by_id(pizza_id: uuid.UUID, db):
    entity = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if entity:
        logging.info('Pizza with id:{} was returned'.format(pizza_id))
    return entity


def get_all_pizzas_of_order(order: Order, db: Session):
    pizza_types = db.query(Pizza.id, PizzaType.name, PizzaType.price, PizzaType.description, PizzaType.dough_id) \
        .join(Pizza.pizza_type) \
        .filter(Pizza.order_id == order.id)

    returnlist: List[JoinedPizzaPizzaTypeSchema] = []
    for pizza_type in pizza_types.all():
        returnlist.append(pizza_type)
    logging.info('returned all pizza from Order:{}'.format(order.id))
    return returnlist


def delete_pizza_from_order(order: Order, pizza_id: uuid.UUID, db: Session):
    entity = db.query(Pizza).filter(Pizza.order_id == order.id, Pizza.id == pizza_id).first()
    if entity:
        db.delete(entity)
        db.commit()
        logging.info('Pizza with id:{} was deleted'.format(pizza_id))
        return True
    else:
        logging.warning('Pizza with id:{} does not exist to be deleted'.format(pizza_id))
        return False


def create_beverage_quantity(
        order: Order,
        schema: OrderBeverageQuantityCreateSchema,
        db: Session,
):
    entity = OrderBeverageQuantity(**schema.dict())
    order.beverages.append(entity)
    db.commit()
    db.refresh(order)
    logging.info('created beverage quantity for order:{}'.format(order.id))
    return entity


def get_beverage_quantity_by_id(
        order_id: uuid.UUID,
        beverage_id: uuid.UUID,
        db: Session,
):
    entity = db.query(OrderBeverageQuantity) \
        .filter(OrderBeverageQuantity.beverage_id == beverage_id,
                OrderBeverageQuantity.order_id == order_id) \
        .first()
    if entity:
        logging.info('Returned beverage quantity for beverage with id:{}, from order with id:{}'
                 .format(beverage_id,order_id))
    else:
        logging.warning('No beverage quantity found for beverage:{}, in Order:{}'.format(beverage_id,order_id))
    return entity


def get_joined_beverage_quantities_by_order(
        order_id: uuid.UUID,
        db: Session,
):
    entities = db.query(OrderBeverageQuantity) \
        .filter(OrderBeverageQuantity.order_id == order_id)
    logging.info('Returned joined beverage quantity for order with id:{}'.format(order_id))
    return entities.all()


def update_beverage_quantity_of_order(order_id: uuid.UUID, beverage_id: uuid.UUID, new_quantity: int, db: Session):
    order_beverage = db.query(OrderBeverageQuantity).filter(order_id == OrderBeverageQuantity.order_id,
                                                            beverage_id == OrderBeverageQuantity.beverage_id).first()
    if order_beverage:
        setattr(order_beverage, 'quantity', new_quantity)
        db.commit()
        db.refresh(order_beverage)
        logging.info('updated beverage quantity from Order:{},quantity to:{}'.format(order_id,new_quantity))

    return order_beverage


def delete_beverage_from_order(order_id: uuid.UUID, beverage_id: uuid.UUID, db: Session):
    entity = db.query(OrderBeverageQuantity).filter(order_id == OrderBeverageQuantity.order_id,
                                                    beverage_id == OrderBeverageQuantity.beverage_id).first()
    if entity:
        db.delete(entity)
        db.commit()
        logging.info('deleted beverage from Order:{},with id:{}'.format(order_id,beverage_id))
        return True
    else:
        logging.warning('No beverage with id:{}, to delete from order with id:{}'.format(beverage_id,order_id))
        return False


def get_price_of_beverage_in_order(order_id: uuid.UUID, db: Session):
    price_beverage: float = 0
    for row in db.query(Beverage.price, OrderBeverageQuantity.quantity) \
            .join(OrderBeverageQuantity) \
            .join(Order) \
            .filter(Order.id == order_id):
        price_beverage += (row.price * row.quantity)
    logging.info('Returned price of beverage from order with id:{}'.format(order_id))
    return price_beverage


def get_price_of_pizza_in_order(order_id: uuid.UUID, db: Session):
    logging.info('Returned price of Pizza from Order with id:{}'.format(order_id))
    return db.query(func.sum(PizzaType.price)) \
        .join(Pizza) \
        .join(Order) \
        .filter(Order.id == order_id).first()[0]


def calculate_price(price_beverage, price_pizza):
    if price_pizza is None:
        logging.info('returned price of beverage alone')
        return price_beverage
    if price_beverage is None:
        logging.info('returned price of Pizza alone')
        return price_pizza
    logging.info('returned price of Pizza and Beverage')
    return price_pizza+price_beverage



def get_price_of_order(
        order_id: uuid.UUID,
        db: Session,
):
    price_beverage: float = get_price_of_beverage_in_order(order_id, db)
    price_pizza = get_price_of_pizza_in_order(order_id, db)
    logging.info('Returned final price of order:{}'.format(order_id))
    return calculate_price(price_beverage, price_pizza)
