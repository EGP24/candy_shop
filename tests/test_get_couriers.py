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


def test_success_get_courier(client):
    client.post('/orders/assign', json={'courier_id': 1})
    time_now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    session = db_session.create_session()
    for order in session.query(Order).filter(Order.delivery_id == 1).all():
        client.post('/orders/complete', json={'courier_id': 1, 'order_id': order.order_id, 'complete_time': time_now})
    rv = client.get('/couriers/1')

    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"foot","earnings":1000,"rating":5.0,"regions":[1,12,22],' \
                      b'"working_hours":["11:35-14:05","09:00-11:00"]}\n'


def test_success_get_courier_without_orders(client):
    client.post('/orders/assign', json={'courier_id': 1})
    rv = client.get('/couriers/1')

    assert rv.status_code == 200
    assert rv.data == b'{"courier_id":1,"courier_type":"foot","earnings":0,"regions":[1,12,22],' \
                      b'"working_hours":["11:35-14:05","09:00-11:00"]}\n'


def test_wrong_courier_id(client):
    client.post('/orders/assign', json={'courier_id': 1})
    rv = client.get('/couriers/5')

    assert rv.status_code == 400
    assert rv.data == b'{"message": "The browser (or proxy) sent a request that this server could not understand."}\n'
