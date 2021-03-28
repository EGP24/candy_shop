from data.time_order_intervals import OrderInterval
from data import db_session


def check_intervals(order_intervals, courier_interval):
    for order_interval in order_intervals:
        time_start_order = order_interval.time_start.hour * 60 + order_interval.time_start.minute
        time_end_order = order_interval.time_end.hour * 60 + order_interval.time_end.minute
        time_end_courier = courier_interval.time_end.hour * 60 + courier_interval.time_end.minute
        time_start_courier = courier_interval.time_start.hour * 60 + courier_interval.time_start.minute
        if set(range(time_start_courier, time_end_courier + 1)) & set(range(time_start_order - 1, time_end_order)):
            return True
    return False


def check_order(order, regions, intervals, sum_weight, carrying):
    session = db_session.create_session()
    order_intervals = session.query(OrderInterval).filter(OrderInterval.order_orm == order).all()
    region_flag = order.region in [region.number_region for region in regions]
    weight_flag = sum_weight + order.weight <= carrying
    interval_flag = any([check_intervals(order_intervals, interval) for interval in intervals])
    return region_flag and weight_flag and interval_flag
