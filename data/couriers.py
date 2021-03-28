from sqlalchemy import orm, Column, Integer, Float, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase, create_session
from .courier_types import CourierType


class Courier(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True, autoincrement=True)
    courier_type = Column(Integer, ForeignKey('courier_types.id'))
    sum_weight = Column(Float, default=0)
    earnings = Column(Integer, default=0)
    delivery_now = Column(Integer, ForeignKey('delivery.id'))

    courier_type_orm = orm.relation('CourierType')
    delivery_orm = orm.relation('Delivery')

    regions_orm = orm.relation('Region', back_populates='courier_orm')
    working_hours_orm = orm.relation('CourierInterval', back_populates='courier_orm')

    @validates('courier_id')
    def validate_courier_id(self, key, value):
        session = create_session()
        ids = [courier.courier_id for courier in session.query(Courier).all()]
        assert value not in ids and isinstance(value, int)
        return value

    @validates('courier_type')
    def validate_courier_type(self, key, value):
        session = create_session()
        types = {courier_type.title: courier_type.id for courier_type in session.query(CourierType).all()}
        assert isinstance(value, str) and value in types
        return types[value]

    @validates('sum_weight')
    def validate_sum_weight(self, key, value):
        assert isinstance(value, (int, float))
        return value

    @validates('earnings')
    def validate_earnings(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('delivery_now')
    def validate_delivery_now(self, key, value):
        assert isinstance(value, int)
        return value
