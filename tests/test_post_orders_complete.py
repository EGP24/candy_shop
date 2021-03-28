from tests.database_functions import reset_db, add_types, add_orders, add_couriers
from datetime import datetime
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
    add_orders(db_session.create_session())
    add_couriers(db_session.create_session())
    with app.test_client() as client:
        yield client
    reset_db(engine)


def test_success_order_complete(client):
    json = {"courier_id": 1, "order_id": 1, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    client.post('/orders/assign', json={"courier_id": 1})
    rv = client.post('/orders/complete', json=json)
    session = db_session.create_session()
    order = session.query(Order).filter(Order.order_id == json['order_id']).first()

    assert rv.status_code == 200
    assert b'{"order_id":1}\n' == rv.data and order.is_complete
    assert order.delivery_orm.get_complete_time() == json['complete_time']


def test_success_double_order_complete(client):
    json_one = {"courier_id": 1, "order_id": 1, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    client.post('/orders/assign', json={"courier_id": 1})
    rv_one = client.post('/orders/complete', json=json_one)
    json_two = {"courier_id": 1, "order_id": 1, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    rv_two = client.post('/orders/complete', json=json_two)
    session = db_session.create_session()
    order = session.query(Order).filter(Order.order_id == json_one['order_id']).first()

    assert rv_one.status_code == rv_two.status_code == 200
    assert b'{"order_id":1}\n' == rv_one.data == rv_two.data and order.is_complete
    assert order.delivery_orm.get_complete_time() == json_one['complete_time']


def test_wrong_courier_id(client):
    json = {"courier_id": 6, "order_id": 1, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_wrong_order_id(client):
    json = {"courier_id": 1, "order_id": 6, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_wrong_complete_time(client):
    json = {"courier_id": 1, "order_id": 1, "complete_time": "datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')"}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_absence_courier_id(client):
    json = {"order_id": 6, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_absence_order_id(client):
    json = {"courier_id": 1, "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_absence_complete_time(client):
    json = {"courier_id": 1, "order_id": 6}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
