from data.time_courier_intervals import CourierInterval
from flask import jsonify, make_response, request
from flask_restful import Resource, abort
from .check_order import check_order
from data.delivery import Delivery
from data.couriers import Courier
from data.regions import Region
from data.orders import Order
from data import db_session


class CouriersListResource(Resource):
    def post(self):
        keys = ['courier_id', 'courier_type', 'working_hours', 'regions']
        session = db_session.create_session()
        not_validated = []
        validated = []

        for courier_data in request.json['data']:
            if not all(key in courier_data for key in keys) or len(courier_data) != len(keys):
                not_validated.append(courier_data['courier_id'])
                continue

            try:
                assert isinstance(courier_data['regions'], list) and isinstance(courier_data['working_hours'], list)
                courier = Courier(courier_id=courier_data['courier_id'], courier_type=courier_data['courier_type'])
                delivery = Delivery(id=courier_data['courier_id'])
                regions = [Region(courier_id=courier_data['courier_id'], number_region=number)
                           for number in courier_data['regions']]
                intervals = [CourierInterval(courier_id=courier_data['courier_id'], time_start=time, time_end=time)
                             for time in courier_data['working_hours']]
                validated.extend([courier, delivery] + regions + intervals)
            except Exception:
                not_validated.append(courier_data['courier_id'])
                continue

        if not_validated:
            return make_response(jsonify({'validation_error': {'couriers': [{'id': id} for id in not_validated]}}), 400)
        for chto_to in validated:
            session.add(chto_to)
        session.commit()
        return make_response(jsonify({'couriers': [
            {'id': courier.courier_id} for courier in filter(lambda x: isinstance(x, Courier), validated)]}), 201)


class CouriersResource(Resource):
    def patch(self, courier_id):
        keys = ['courier_type', 'regions', 'working_hours']
        if not courier_id.isdigit():
            abort(400)
        courier_id = int(courier_id)

        session = db_session.create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).first()

        if any(key not in keys for key in request.json.keys()) or not courier:
            abort(400)

        try:
            if 'courier_type' in request.json:
                courier.courier_type = request.json['courier_type']

            if 'regions' in request.json:
                assert isinstance(request.json['regions'], list)
                courier_regions = {region.number_region: region for region in session.query(Region).filter(
                    Region.courier_orm == courier).all()}
                for key, value in courier_regions.items():
                    if key not in request.json['regions']:
                        session.delete(value)

                for region in request.json['regions']:
                    if region not in courier_regions:
                        session.add(Region(courier_id=courier_id, number_region=region))

            if 'working_hours' in request.json:
                assert isinstance(request.json['working_hours'], list)
                courier_intervals = {str(interval): interval for interval in session.query(CourierInterval).filter(
                    CourierInterval.courier_orm == courier).all()}
                for key, value in courier_intervals.items():
                    if key not in request.json['working_hours']:
                        session.delete(value)

                for interval in request.json['working_hours']:
                    if interval not in courier_intervals:
                        session.add(CourierInterval(courier_id=courier_id, time_start=interval, time_end=interval))
        except Exception:
            abort(400)
        session.commit()

        orders = sorted(session.query(Order).filter(Order.delivery_orm == courier.delivery_orm,
                                                    Order.is_complete == 0).all(), key=lambda x: x.weight)
        courier_regions = session.query(Region).filter(Region.courier_orm == courier).all()
        courier_intervals = session.query(CourierInterval).filter(CourierInterval.courier_orm == courier).all()
        courier_carrying = courier.courier_type_orm.carrying
        courier_sum_weight = 0
        for order in orders:
            try:
                if not check_order(order, courier_regions, courier_intervals, courier_sum_weight, courier_carrying):
                    order.delivery_id = None
                else:
                    courier_sum_weight += order.weight
            except Exception:
                abort(400)
        courier.sum_weight = courier_sum_weight
        session.commit()
        return make_response(jsonify(
            {'courier_id': courier.courier_id,
             'courier_type': courier.courier_type_orm.title,
             'regions': [x.number_region for x in session.query(Region).filter(Region.courier_orm == courier).all()],
             'working_hours': [str(x) for x in session.query(CourierInterval).filter(
                 CourierInterval.courier_orm == courier).all()]}))

    def get(self, courier_id):
        if not courier_id.isdigit():
            abort(400)
        courier_id = int(courier_id)
        session = db_session.create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).first()
        if not courier:
            abort(400)

        courier_regions = [r.number_region for r in session.query(Region).filter(Region.courier_orm == courier)]
        working_hours = [str(i) for i in session.query(CourierInterval).filter(CourierInterval.courier_orm == courier)]
        courier_data = {'courier_id': courier_id, 'courier_type': courier.courier_type_orm.title,
                        'earnings': courier.earnings, 'regions': courier_regions, 'working_hours': working_hours}
        if courier.earnings:
            regions = session.query(Region).filter(Region.courier_orm == courier, Region.orders_count != 0).all()
            min_delivery_time = min([60 * 60] + [region.sum_time / region.orders_count for region in regions])
            rating = (60 * 60 - min_delivery_time) / 60 / 60 * 5
            courier_data['rating'] = round(rating, 2)
        return make_response(jsonify(courier_data))
