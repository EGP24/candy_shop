from tests.database_functions import reset_db, add_types, add_orders, add_couriers
from datetime import datetime
from data.orders import Order
from data import db_session
from os.path import exists
from json import loads
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


def test_success_order_assign(client):
    json = {"courier_id": 1}
    rv = client.post('/orders/assign', json=json)
    rv_dict = loads(rv.data)
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.delivery_id == json['courier_id']).all()

    assert rv.status_code == 200
    assert 'assign_time' in rv_dict and rv_dict['orders'] == [{'id': 3}, {'id': 1}]
    assert sorted([order.order_id for order in orders]) == [1, 3]
    assert all([order.delivery_id is not None for order in orders])
    assert all([str(order.delivery_orm) == rv_dict['assign_time'] for order in orders])


def test_success_double_assign(client):
    json = {"courier_id": 1}
    rv_one = client.post('/orders/assign', json=json)
    rv_one_dict = loads(rv_one.data)
    rv_two = client.post('/orders/assign', json=json)
    rv_two_dict = loads(rv_one.data)
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.delivery_id == json['courier_id']).all()

    assert rv_one.status_code == rv_two.status_code == 200
    assert 'assign_time' in rv_one_dict and rv_one_dict['orders'] == [{'id': 3}, {'id': 1}]
    assert 'assign_time' in rv_two_dict and rv_two_dict['orders'] == [{'id': 3}, {'id': 1}]
    assert sorted([order.order_id for order in orders]) == [1, 3]
    assert all([order.delivery_id is not None for order in orders])
    assert all([str(order.delivery_orm) == rv_one_dict['assign_time'] for order in orders])


def test_success_double_assign_with_complete(client):
    json = {"courier_id": 1}
    rv_one = client.post('/orders/assign', json=json)
    rv_one_dict = loads(rv_one.data)
    client.post('/orders/complete', json={"courier_id": 1, "order_id": 3,
                                          "complete_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')})

    rv_two = client.post('/orders/assign', json={"courier_id": 1})
    rv_two_dict = loads(rv_two.data)
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.delivery_id == json['courier_id']).all()

    assert rv_one.status_code == rv_two.status_code == 200
    assert 'assign_time' in rv_one_dict and rv_one_dict['orders'] == [{'id': 3}, {'id': 1}]
    assert 'assign_time' in rv_two_dict and rv_two_dict['orders'] == [{'id': 1}]
    assert sorted([order.order_id for order in orders]) == [1, 3]
    assert all([order.delivery_id is not None for order in orders])
    assert all([str(order.delivery_orm) == rv_one_dict['assign_time'] for order in orders])


def test_null_order_assign(client):
    json = {"courier_id": 3}
    rv = client.post('/orders/assign', json=json)
    rv_dict = loads(rv.data)
    session = db_session.create_session()
    orders = [{'id': od.order_id} for od in session.query(Order).filter(Order.delivery_id == json['courier_id']).all()]

    assert rv.status_code == 200
    assert 'assign_time' not in rv_dict and rv_dict['orders'] == []
    assert sorted(orders) == []


def test_wrong_courier_id(client):
    json = {"courier_id": 4}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_absence_courier_id(client):
    json = {}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'


def test_not_specified_field(client):
    json = {'courier_id': 2, 'kek': 'lol'}
    rv = client.post('/orders/assign', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
