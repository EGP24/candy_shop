from sqlalchemy import orm, Column, Integer, DateTime, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase, create_session
from .courier_types import CourierType
from datetime import datetime


class Delivery(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'delivery'

    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_type = Column(Integer,  ForeignKey('courier_types.id'))
    assign_time = Column(DateTime)
    complete_time = Column(DateTime)

    courier_type_orm = orm.relation('CourierType')

    courier_orm = orm.relation('Courier', back_populates='delivery_orm')
    order_orm = orm.relation('Order', back_populates='delivery_orm')

    def __str__(self):
        return self.assign_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    @validates('id')
    def validate_id(self, key, value):
        session = create_session()
        ids = [delivery.id for delivery in session.query(Delivery).all()]
        assert value not in ids and isinstance(value, int)
        return value

    @validates('courier_type')
    def validate_courier_type(self, key, value):
        session = create_session()
        types = {courier_type.title: courier_type.id for courier_type in session.query(CourierType).all()}
        assert value in types
        return types[value]

    @validates('assign_time')
    def validate_assign_time(self, key, value):
        if value is not None:
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        return value

    @validates('complete_time')
    def validate_complete_time(self, key, value):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        return value



