from data.courier_types import CourierType
from resources import courier_resource
from resources import order_resource
from flask_restful import Api
from data import db_session
from os.path import exists
from waitress import serve
from flask import Flask
from os import mkdir


def add_courier_types():
    session = db_session.create_session()
    if sorted(type.title for type in session.query(CourierType).all()) != ['bike', 'car', 'foot']:
        session.query(CourierType).delete()
        session.commit()
        types = ((1, 'foot', 10, 2), (2, 'bike', 15, 5), (3, 'car', 50, 9))
        for id, title, carrying, coefficient in types:
            type = CourierType(id=id, title=title, carrying=carrying, coefficient=coefficient)
            session.add(type)
        session.commit()


app = Flask(__name__)
api = Api(app)

api.add_resource(courier_resource.CouriersResource, '/couriers/<string:courier_id>')
api.add_resource(order_resource.OrderCompleteResource, '/orders/complete')
api.add_resource(order_resource.OrdersAssignResource, '/orders/assign')
api.add_resource(courier_resource.CouriersListResource, '/couriers')
api.add_resource(order_resource.OrdersListResource, '/orders')


def main():
    if not exists('./db'):
        mkdir('./db')
    db_session.global_init('db/base.db')
    add_courier_types()

    serve(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
