from data.time_courier_intervals import CourierInterval
from tests.database_functions import reset_db, add_types
from data.couriers import Courier
from data.regions import Region
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


def test_success_add_couriers(client):
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
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        },
        {
            "courier_id": 3,
            "courier_type": "car",
            "regions": [12, 22, 23, 33],
            "working_hours": []
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 201
    assert rv.data == b'{"couriers":[{"id":1},{"id":2},{"id":3}]}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        c_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
        c_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
        assert courier is not None
        assert courier.courier_type_orm.title == courier_data['courier_type']
        assert sorted(c_regions) == sorted(courier_data['regions'])
        assert sorted(c_hours) == sorted(courier_data['working_hours'])


def test_unique_courier_id(client):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 201
    assert rv.data == b'{"couriers":[{"id":1}]}\n'

    courier = session.query(Courier).filter(Courier.courier_id == json['data'][0]['courier_id']).first()
    c_regions = [reg.number_region for reg in session.query(Region).filter(Region.courier_orm == courier).all()]
    c_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()]
    assert courier is not None and courier.courier_type_orm.title == json['data'][0]['courier_type']
    assert sorted(c_regions) == sorted(json['data'][0]['regions'])
    assert sorted(c_hours) == sorted(json['data'][0]['working_hours'])

    rv = client.post('/couriers', json=json)

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1}]}}\n'


def test_wrong_courier_id(client):
    json = {"data": [
        {
            "courier_id": '1',
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":"1"}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_wrong_courier_type(client):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "",
            "regions": 1,
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_wrong_courier_regions(client):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, '22'],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": '',
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1},{"id":2}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_wrong_courier_working_hours(client):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ''
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:0f0-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1},{"id":2}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_absence_courier_type(client):
    json = {"data": [
        {
            "courier_id": 1,
            "regions": 1,
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_absence_courier_regions(client):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_absence_courier_working_hours(client):
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None


def test_not_specified_fields(client):
    session = db_session.create_session()
    json = {"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"],
            "pereverza_vlados_checkindos_228": 1
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None
