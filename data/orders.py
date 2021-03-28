from sqlalchemy import orm, Column, Integer, Boolean, Float, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase, create_session
from .delivery import Delivery


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_id = Column(Integer, ForeignKey('delivery.id'))
    weight = Column(Float)
    region = Column(Integer)
    is_complete = Column(Boolean, default=False)

    delivery_orm = orm.relation('Delivery')

    delivery_hours_orm = orm.relation('OrderInterval', back_populates='order_orm')

    @validates('order_id')
    def validate_order_id(self, key, value):
        session = create_session()
        ids = [order.order_id for order in session.query(Order).all()]
        assert value not in ids and isinstance(value, int)
        return value

    @validates('weight')
    def validate_weight(self, key, value):
        assert isinstance(value, (int, float)) and 0.01 <= value <= 50 and value == round(value, 2)
        return value

    @validates('region')
    def validate_region(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('delivery_id')
    def validate_delivery_id(self, key, value):
        session = create_session()
        ids = [delivery.id for delivery in session.query(Delivery).all()]
        assert isinstance(value, int) and value in ids or value is None
        return value

    @validates('is_complete')
    def validate_is_complete(self, key, value):
        assert isinstance(value, bool)
        return value
