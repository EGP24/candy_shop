from data import db_session
from data.couriers import Courier
from data.regions import Region
from data.courier_types import CourierType
from data.time_courier_intervals import CourierInterval
from app import app
import pytest
from data.db_session import SqlAlchemyBase


def add_types(session):
    types = (('foot', 10, 2), ('bike', 15, 5), ('car', 50, 9))
    for title, carrying, coefficient in types:
        typee = CourierType(title=title, carrying=carrying, coefficient=coefficient)
        session.add(typee)
    session.commit()


def reset_db(engine):
    SqlAlchemyBase.metadata.drop_all(engine)
    SqlAlchemyBase.metadata.create_all(engine)


@pytest.fixture()
def client():
    engine = db_session.global_init('../db/test_base.db')
    reset_db(engine)
    app.config['TESTING'] = True
    add_types(db_session.create_session())
    with app.test_client() as client:
        yield client


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


def test_wrong_field_courier(client):
    json = {"data": [
        {
            "courier_id": 1,
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "couriefdsr_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        },
        {
            "courier_id": 3,
            "courier_type": "car",
            "working_hours": []
        }
    ]}
    rv = client.post('/couriers', json=json)
    session = db_session.create_session()

    assert rv.status_code == 400
    assert rv.data == b'{"validation_error":{"couriers":[{"id":1},{"id":2},{"id":3}]}}\n'
    for courier_data in json['data']:
        courier = session.query(Courier).filter(Courier.courier_id == courier_data['courier_id']).first()
        assert courier is None



