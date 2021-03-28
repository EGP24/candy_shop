from data.time_courier_intervals import CourierInterval
from data.time_order_intervals import OrderInterval
from data.db_session import SqlAlchemyBase
from data.courier_types import CourierType
from data.delivery import Delivery
from data.couriers import Courier
from data.regions import Region
from data.orders import Order


def add_types(session):
    types = (('foot', 10, 2), ('bike', 15, 5), ('car', 50, 9))
    for title, carrying, coefficient in types:
        typee = CourierType(title=title, carrying=carrying, coefficient=coefficient)
        session.add(typee)
    session.commit()


def reset_db(engine):
    SqlAlchemyBase.metadata.drop_all(engine)
    SqlAlchemyBase.metadata.create_all(engine)


def add_couriers(session):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [1],
            "working_hours": ["09:00-18:00"]
        },
        {
            "courier_id": 3,
            "courier_type": "car",
            "regions": [12, 22, 23, 33],
            "working_hours": []
        }]}
    validated = []
    for courier_data in json['data']:
        courier = Courier(courier_id=courier_data['courier_id'], courier_type=courier_data['courier_type'])
        delivery = Delivery(id=courier_data['courier_id'])
        regions = [Region(courier_id=courier_data['courier_id'], number_region=number)
                   for number in courier_data['regions']]
        intervals = [CourierInterval(courier_id=courier_data['courier_id'], time_start=time, time_end=time)
                     for time in courier_data['working_hours']]
        validated.extend([courier, delivery] + regions + intervals)
    for chto_to in validated:
        session.add(chto_to)
    session.commit()


def add_orders(session):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 12,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        }]}
    validated = []
    for order_data in json['data']:
        order = Order(order_id=order_data['order_id'], weight=order_data['weight'], region=order_data['region'])
        intervals = [OrderInterval(order_id=order_data['order_id'], time_start=time, time_end=time)
                     for time in order_data['delivery_hours']]
        validated.extend([order] + intervals)
    for chto_to in validated:
        session.add(chto_to)
    session.commit()
