from sqlalchemy import orm, Column, Integer, Time, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase, create_session
from datetime import datetime


class CourierInterval(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'courier_intervals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_id = Column(Integer, ForeignKey('couriers.courier_id'))
    time_start = Column(Time)
    time_end = Column(Time)

    courier_orm = orm.relation('Courier')

    def __str__(self):
        return f'{self.time_start.strftime("%H:%M")}-{self.time_end.strftime("%H:%M")}'

    @validates('id')
    def validate_id(self, key, value):
        session = create_session()
        ids = [interval.id for interval in session.query(CourierInterval).all()]
        assert value not in ids
        return value

    @validates('courier_id')
    def validate_courier_id(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('time_start')
    def validate_time_start(self, key, value):
        time_start = datetime.strptime(value.split('-')[0], '%H:%M').time()
        return time_start

    @validates('time_end')
    def validate_time_end(self, key, value):
        time_end = datetime.strptime(value.split('-')[1], '%H:%M').time()
        return time_end
