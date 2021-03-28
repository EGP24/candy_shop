from tests.database_functions import reset_db, add_types
from data.time_order_intervals import OrderInterval
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
    with app.test_client() as client:
        yield client
    reset_db(engine)


def test_success_add_orders(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 201
    assert rv.data == b'{"orders":[{"id":1},{"id":2},{"id":3}]}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        o_hours = [str(i) for i in session.query(OrderInterval).filter(OrderInterval.order_orm == order).all()]
        assert order is not None
        assert order.weight == order_data['weight']
        assert order.region == order_data['region']
        assert sorted(o_hours) == sorted(order_data['delivery_hours'])


def test_unique_order_id(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 201
    assert rv.data == b'{"orders":[{"id":1}]}\n'

    order = session.query(Order).filter(Order.order_id == json['data'][0]['order_id']).first()
    o_hours = [str(i) for i in session.query(OrderInterval).filter(OrderInterval.order_orm == order).all()]
    assert order is not None and order.weight == json['data'][0]['weight']
    assert order.region == json['data'][0]['region']
    assert sorted(o_hours) == sorted(json['data'][0]['delivery_hours'])

    rv = client.post('/orders', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1}]}}\n'


def test_wrong_order_id(client):
    json = {"data": [
        {
            "order_id": "1",
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":"1"}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_wrong_order_weight(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.099,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 50.01,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": "",
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1},{"id":2},{"id":3}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_wrong_order_region(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": "12",
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_wrong_order_delivery_hours(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": 'jjj'
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:0f0-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1},{"id":2}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_absence_order_weight(client):
    json = {"data": [
        {
            "order_id": 1,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_absence_order_region(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_absence_order_delivery_hours(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None


def test_not_specified_fields(client):
    json = {"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"],
            "kek": "lol"
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/orders', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"orders":[{"id":1}]}}\n'
    for order_data in json['data']:
        order = session.query(Order).filter(Order.order_id == order_data['order_id']).first()
        assert order is None
