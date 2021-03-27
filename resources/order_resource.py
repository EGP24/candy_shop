from flask_restful import Resource, abort
from flask import jsonify, make_response, request
from data import db_session
from data.couriers import Courier
from data.regions import Region
from data.delivery import Delivery
from data.time_courier_intervals import CourierInterval
from data.time_order_intervals import OrderInterval
from data.orders import Order
from .check_order import check_order
from datetime import datetime


class OrdersListResource(Resource):
    def post(self):
        keys = ['order_id', 'weight', 'region', 'delivery_hours']
        session = db_session.create_session()
        not_validated = []
        validated = []

        for order_data in request.json['data']:
            if not all(key in order_data for key in keys) or len(order_data) != len(keys):
                not_validated.append(order_data['order_id'])
                continue

            try:
                order = Order(order_id=order_data['order_id'], weight=order_data['weight'], region=order_data['region'])
                intervals = [OrderInterval(order_id=order_data['order_id'], time_start=time, time_end=time)
                             for time in order_data['delivery_hours']]
                validated.extend([order] + intervals)
            except Exception as e:
                not_validated.append(order_data['order_id'])
                continue

        if not_validated:
            return make_response(jsonify({'validation_error': {'orders': [{'id': id} for id in not_validated]}}), 400)
        for chto_to in validated:
            session.add(chto_to)
        session.commit()
        return make_response(jsonify({'orders': [
            {'id': order.order_id} for order in filter(lambda x: isinstance(x, Order), validated)]}), 201)


class OrdersAssignResource(Resource):
    def post(self):
        session = db_session.create_session()
        assign_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        if len(request.json) != 1 or list(request.json.keys())[0] != 'courier_id':
            abort(400)
        courier = session.query(Courier).filter(Courier.courier_id == request.json['courier_id']).first()
        if not courier:
            abort(400)

        orders = session.query(Order).filter(Order.delivery_id != None, Order.delivery_id == courier.delivery_now, Order.is_complete != 1).all()
        if orders:
            return make_response(jsonify({'orders': [{'id': id} for id in [order.order_id for order in orders]],
                                          'assign_time': str(orders[0].delivery_orm)}))
        orders = sorted(session.query(Order).filter(Order.delivery_id == None, Order.is_complete == 0).all(),
                        key=lambda order: order.weight)
        courier_regions = session.query(Region).filter(Region.courier_orm == courier).all()
        courier_intervals = session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()
        courier_sum_weight = courier.sum_weight
        courier_carrying = courier.courier_type_orm.carrying
        orders_assign = []
        for order in orders:
            if check_order(order, courier_regions, courier_intervals, courier_sum_weight, courier_carrying):
                try:
                    orders_assign.append(order)
                    courier_sum_weight += order.weight
                except Exception:
                    abort(400)
        courier.sum_weight = courier_sum_weight
        if orders_assign:
            delivery = session.query(Delivery).filter(Delivery.id == courier.courier_id).first()
            delivery.assign_time = assign_time
            delivery.courier_type = courier.courier_type_orm.title
            courier.delivery_now = delivery.id
            if delivery.complete_time is None:
                delivery.complete_time = assign_time
            for order in orders_assign:
                order.delivery_id = delivery.id
            session.commit()
            return make_response(jsonify({'orders': [{'id': id} for id in [order.order_id for order in orders_assign]],
                                          'assign_time': assign_time}), 200)
        return make_response(jsonify({'orders': []}), 200)


class OrderCompleteResource(Resource):
    def post(self):
        session = db_session.create_session()

        if not ('courier_id' in request.json and 'order_id' in request.json and 'complete_time' in request.json):
            abort(400)
        courier = session.query(Courier).filter(Courier.courier_id == request.json['courier_id']).first()
        if not courier:
            abort(400)
        order = session.query(Order).filter(Order.delivery_orm == courier.delivery_orm,
                                            Order.order_id == request.json['order_id']).first()
        if not order:
            abort(400)

        if not order.is_complete:
            try:
                delivery_time = (datetime.strptime(request.json['complete_time'], '%Y-%m-%dT%H:%M:%S.%fZ') -
                                 courier.delivery_orm.complete_time).total_seconds()

                order.is_complete = True
                courier.sum_weight -= order.weight
                region = session.query(Region).filter(Region.number_region == order.region,
                                                      Region.courier_orm == courier).first()
                region.orders_count += 1
                region.sum_time += delivery_time
                courier.delivery_orm.complete_time = request.json['complete_time']
            except Exception:
                abort(400)
            session.commit()
            delivery_orders = session.query(Order).filter(Order.delivery_orm == courier.delivery_orm,
                                                          Order.is_complete == 0).all()

            if not delivery_orders:
                courier.earnings += 500 * courier.delivery_orm.courier_type_orm.coefficient
                session.commit()

        return make_response(jsonify({'order_id': order.order_id}))
