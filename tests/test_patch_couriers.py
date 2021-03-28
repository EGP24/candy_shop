from tests.database_functions import reset_db, add_types, add_couriers, add_orders
from data.time_courier_intervals import CourierInterval
from data.couriers import Courier
from data.regions import Region
from data.orders import Order
from data import db_session
from os.path import exists
from os import mkdir
from app import app
import pytest


@pytest.fixture()
def client():
    if not exists('./db'):
        mkdir('./db')
    engine = db_session.global_init('./db/test_base.db')
    app.config['TESTING'] = True
    add_types(db_session.create_session())
    add_couriers(db_session.create_session())
    add_orders(db_session.create_session())
    with app.test_client() as client:
        yield client
    reset_db(engine)


def test_wrong_courier_id(client):
    json = {"courier_type": "car", "regions": [1], "working_hours": ["11:20-14:05"], "kek": "lol"}
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    cr_type = courier.courier_type_orm.title
    cr_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    cr_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    rv = client.patch('/couriers/dfg', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
    n_cr_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    n_cr_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert courier is not None
    assert courier.courier_type_orm.title == cr_type
    assert sorted(n_cr_regions) == sorted(cr_regions)
    assert sorted(n_cr_hours) == sorted(cr_hours)


def test_success_edit_courier_type(client):
    json = {"courier_type": "car"}
    rv = client.patch('/couriers/1', json=json)
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()

    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"car","regions":[1,12,22],' \
                      b'"working_hours":["11:35-14:05","09:00-11:00"]}\n'
    assert courier is not None and courier.courier_type_orm.title == json['courier_type']


def test_success_edit_regions(client):
    json = {"regions": [1]}
    rv = client.patch('/couriers/1', json=json)
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()

    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"foot","regions":[1],' \
                      b'"working_hours":["11:35-14:05","09:00-11:00"]}\n'
    courier_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    assert courier is not None and sorted(courier_regions) == sorted(json['regions'])


def test_success_edit_working_hours(client):
    json = {"working_hours": ["11:20-14:05"]}
    rv = client.patch('/couriers/1', json=json)
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()

    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"foot","regions":[1,12,22],"working_hours":["11:20-14:05"]}\n'
    c_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert courier is not None and sorted(c_hours) == sorted(json['working_hours'])


def test_success_edit_courier(client):
    json = {"courier_type": "car", "regions": [1], "working_hours": ["11:20-14:05"]}
    rv = client.patch('/couriers/1', json=json)
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()

    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"car","regions":[1],"working_hours":["11:20-14:05"]}\n'
    c_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    c_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert courier is not None
    assert courier.courier_type_orm.title == json['courier_type']
    assert sorted(c_regions) == sorted(json['regions'])
    assert sorted(c_hours) == sorted(json['working_hours'])


def test_wrong_courier_type(client):
    json = {"courier_type": "kek"}
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    courier_type = courier.courier_type_orm.title
    rv = client.patch('/couriers/1', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
    assert courier is not None and courier.courier_type_orm.title == courier_type


def test_wrong_courier_regions(client):
    json = {"courier_regions": ["kek", 2, 3, 4]}
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    courier_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    rv = client.patch('/couriers/1', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
    assert courier is not None
    n_courier_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    assert sorted(n_courier_regions) == sorted(courier_regions)


def test_wrong_courier_working_hours(client):
    json = {"courier_regions": '["kek", "11:35-14:05", "09:00-11:00"]'}
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    cr_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    rv = client.patch('/couriers/1', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
    assert courier is not None
    n_cr_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert sorted(n_cr_hours) == sorted(cr_hours)


def test_not_specified_field(client):
    json = {"courier_type": "car", "regions": [1], "working_hours": ["11:20-14:05"], "kek": "lol"}
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    cr_type = courier.courier_type_orm.title
    cr_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    cr_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    rv = client.patch('/couriers/1', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
    n_cr_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    n_cr_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert courier is not None
    assert courier.courier_type_orm.title == cr_type
    assert sorted(n_cr_regions) == sorted(cr_regions)
    assert sorted(n_cr_hours) == sorted(cr_hours)


def test_success_edit_courier_type_with_unassign_orders(client):
    json = {"courier_type": "foot"}
    client.post('/orders/assign', json={'courier_id': 2})
    session = db_session.create_session()

    assert sorted(order.order_id for order in session.query(Order).filter(Order.delivery_id == 2)) == [2]
    rv = client.patch('/couriers/2', json=json)
    courier = session.query(Courier).filter(Courier.courier_id == 2).first()
    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":2,"courier_type":"foot","regions":[1],"working_hours":["09:00-18:00"]}\n'
    assert courier is not None and courier.courier_type_orm.title == json['courier_type']
    assert [order.order_id for order in session.query(Order).filter(Order.delivery_id == 2)] == []


def test_success_edit_courier_regions_with_unassign_orders(client):
    json = {"regions": [1]}
    client.post('/orders/assign', json={'courier_id': 1})
    session = db_session.create_session()

    assert sorted(order.order_id for order in session.query(Order).filter(Order.delivery_id == 1)) == [1, 3]
    rv = client.patch('/couriers/1', json=json)
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"foot","regions":[1],' \
                      b'"working_hours":["11:35-14:05","09:00-11:00"]}\n'
    courier_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    assert courier is not None and sorted(courier_regions) == sorted(json['regions'])
    assert [order.order_id for order in session.query(Order).filter(Order.delivery_id == 1)] == []


def test_success_edit_courier_working_hours_unassign_orders(client):
    json = {"working_hours": ["21:30-21:40"]}
    client.post('/orders/assign', json={'courier_id': 1})
    session = db_session.create_session()

    assert sorted(order.order_id for order in session.query(Order).filter(Order.delivery_id == 1)) == [1, 3]
    rv = client.patch('/couriers/1', json=json)
    courier = session.query(Courier).filter(Courier.courier_id == 1).first()
    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"foot","regions":[1,12,22],"working_hours":["21:30-21:40"]}\n'
    c_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert courier is not None and sorted(c_hours) == sorted(json['working_hours'])
    assert [order.order_id for order in session.query(Order).filter(Order.delivery_id == 1)] == []
