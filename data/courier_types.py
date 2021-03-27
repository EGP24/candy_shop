import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_session import SqlAlchemyBase, create_session


class CourierType(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'courier_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    carrying = sqlalchemy.Column(sqlalchemy.Integer)
    coefficient = sqlalchemy.Column(sqlalchemy.Integer)

    courier_orm = orm.relation('Courier', back_populates='courier_type_orm')
    delivery_orm = orm.relation('Delivery', back_populates='courier_type_orm')

    @validates('id')
    def validate_id(self, key, value):
        session = create_session()
        ids = [courier_type.id for courier_type in session.query(CourierType).all()]
        assert value in ids
        return value

    @validates('title')
    def validate_title(self, key, value):
        assert isinstance(value, str)
        return value

    @validates('carrying')
    def validate_carrying(self, key, value):
        assert isinstance(value, int)
        return value

    @validates('coefficient')
    def validate_coefficient(self, key, value):
        assert isinstance(value, int)
        return value
