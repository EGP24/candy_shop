from flask_restful import Api
from flask import Flask
from data import db_session
from resources import courier_resource
from resources import order_resource
import os

app = Flask(__name__)
api = Api(app)

api.add_resource(courier_resource.CouriersListResource, '/couriers')
api.add_resource(courier_resource.CouriersResource, '/couriers/<int:courier_id>')
api.add_resource(order_resource.OrdersListResource, '/orders')
api.add_resource(order_resource.OrdersAssignResource, '/orders/assign')
api.add_resource(order_resource.OrderCompleteResource, '/orders/complete')


def main():
    db_session.global_init('db/base.db')
    # TODO : Сменить порт и хост
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()