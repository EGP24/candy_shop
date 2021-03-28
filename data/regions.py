from sqlalchemy import orm, Column, Integer, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase, create_session


class Region(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number_region = Column(Integer)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    orders_count = Column(Integer, default=0)
    sum_time = Column(Integer, default=0)

    courier_orm = orm.relation('Courier')

    @validates('id')
    def validate_id(self, key, value):
        session = create_session()
        ids = [region.id for region in session.query(Region).all()]
        assert value in ids
        return value

    @validates('number_region')
    def validate_number_region(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('courier_id')
    def validate_courier_id(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('orders_count')
    def validate_orders_count(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('sum_time')
    def validate_sum_time(self, key, value):
        assert isinstance(value, (int, float))
        return value
