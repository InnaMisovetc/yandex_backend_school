import json

from django.test import TestCase, Client
from django.urls import reverse
import datetime


couriers_json = {"data": [
    {"courier_id": 1, "courier_type": "foot", "regions": [5, 12, 22], "working_hours": ["11:35-14:55"]},
    {"courier_id": 2, "courier_type": "car", "regions": [23, 35, 42], "working_hours": ["12:00-14:40", "16:00-18:00"]},
    {"courier_id": 3, "courier_type": "bike", "regions": [1, 10, 56], "working_hours": ["8:00-10:00"]},
    {"courier_id": 4, "courier_type": "car", "regions": [2, 13, 37], "working_hours": ["9:00-13:00"]},
    {"courier_id": 5, "courier_type": "foot", "regions": [1, 40, 59], "working_hours": ["12:00-18:00"]},
    {"courier_id": 6, "courier_type": "bike", "regions": [3, 7, 11], "working_hours": ["9:00-13:00", "15:00-19:00"]},
    {"courier_id": 7, "courier_type": "bike", "regions": [13, 43, 38], "working_hours": ["17:00-22:00"]},
    {"courier_id": 8, "courier_type": "foot", "regions": [4, 6, 23], "working_hours": ["7:00-10:00", "20:00-23:00"]},
    {"courier_id": 9, "courier_type": "car", "regions": [2, 9, 55], "working_hours": ["10:00-19:00"]}]}

orders_json = {"data": [
    {"order_id": 4, "weight": 0.23, "region": 1, "delivery_hours": ["9:00-15:00"]},
    {"order_id": 5, "weight": 1, "region": 5, "delivery_hours": ["12:00-14:30"]},
    {"order_id": 10, "weight": 3, "region": 10, "delivery_hours": ["8:00-14:40"]},
    {"order_id": 12, "weight": 8, "region": 23, "delivery_hours": ["10:00-15:00"]},
    {"order_id": 20, "weight": 12, "region": 30, "delivery_hours": ["12:00-16:00"]},
    {"order_id": 35, "weight": 4.55, "region": 35, "delivery_hours": ["17:00-20:00"]},
    {"order_id": 38, "weight": 18, "region": 56, "delivery_hours": ["20:00-22:00"]},
    {"order_id": 39, "weight": 22.5, "region": 42, "delivery_hours": ["10:00-12:00"]},
    {"order_id": 40, "weight": 50.0, "region": 35, "delivery_hours": ["15:00-20:00", "22:00-23:00"]}]}

couriers_url = reverse('import_couriers')
orders_url = reverse('import_orders')
assign_orders_url = reverse('assign_orders')
complete_order_url = reverse('complete_order')


class TestCouriersView(TestCase):
    couriers_json_good = {'data': [{"courier_id": 10, "courier_type": "foot", "regions": [14, 33, 43],
                                    "working_hours": ["11:30-14:00", "18:00-21:00"]},
                                   {"courier_id": 11, "courier_type": "car", "regions": [23, 32, 44],
                                    "working_hours": ["8:30-14:00"]}]}
    couriers_json_id_already_exists = {'data': [
        {"courier_id": 1, "courier_type": "foot", "regions": [1, 12, 22],
         "working_hours": ["11:35-14:05", "18:00-19:00"]}]}
    couriers_json_invalid_id = {'data': [
        {"courier_id": 'text', "courier_type": "foot", "regions": [1, 12, 22], "working_hours": ["11:35-14:05"]}]}
    couriers_json_invalid_type = {'data': [
        {"courier_id": 5, "courier_type": 5, "regions": [1, 12, 22], "working_hours": ["11:35-14:05"]}]}
    couriers_json_invalid_regions = {'data': [
        {"courier_id": 5, "courier_type": "run", "regions": [1, 12, -2], "working_hours": ["11:35-14:05"]}]}
    couriers_json_invalid_working_hours = {'data': [
        {"courier_id": 5, "courier_type": "run", "regions": [5, 12, 32], "working_hours": ["11:35-14:99"]}]}

    def setUp(self):
        self.client = Client()
        self.client.post(couriers_url,
                         data=json.dumps(couriers_json).encode('utf-8'),
                         content_type='application/json')

    def addCourier(self, input_dict):
        return self.client.post(couriers_url,
                                data=json.dumps(input_dict).encode('utf-8'),
                                content_type='application/json')

    def test_couriers_json_good(self):
        response = self.addCourier(self.couriers_json_good)
        self.assertEquals(response.status_code, 201)

    def test_couriers_json_invalid_id(self):
        response = self.addCourier(self.couriers_json_invalid_id)
        self.assertEquals(response.status_code, 400)

    def test_couriers_json_invalid_type(self):
        response = self.addCourier(self.couriers_json_invalid_type)
        self.assertEquals(response.status_code, 400)

    def test_couriers_json_invalid_regions(self):
        response = self.addCourier(self.couriers_json_invalid_regions)
        self.assertEquals(response.status_code, 400)

    def test_couriers_json_invalid_working_hours(self):
        response = self.addCourier(self.couriers_json_invalid_working_hours)
        self.assertEquals(response.status_code, 400)

    def test_couriers_json_id_already_exists(self):
        response = self.addCourier(self.couriers_json_id_already_exists)
        self.assertEquals(response.status_code, 400)


class TestCourierView(TestCase):
    patch_json_good_one = {"working_hours": ["11:35-14:05"]}
    patch_json_good_two = {"courier_type": "foot"}
    patch_json_invalid_value = {"courier_type": "big_foot",
                                "regions": [1, 12, 22],
                                "working_hours": ["11:35-14:05"]}
    patch_json_invalid_field = {"my_courier_type": "foot",
                                "regions": [1, 12, 22],
                                "working_hours": ["11:35-14:05"]}
    patch_json_plus_id_bad = {'courier_id': 1,
                              "courier_type": "foot",
                              "regions": [1, 12, 22],
                              "working_hours": ["11:35-14:05"]}
    courier_one_inf = {"courier_id": 1, "courier_type": "foot", "regions": [5, 12, 22],
                       "working_hours": ["11:35-14:55"], 'earnings': 0}

    def setUp(self):
        self.client = Client()
        self.client.post(couriers_url,
                         data=json.dumps(couriers_json).encode('utf-8'),
                         content_type='application/json')

    def modifyCourier(self, input_dict, courier_id):
        courier_url = reverse('modify_courier', args=[courier_id])
        return self.client.patch(courier_url,
                                 data=json.dumps(input_dict).encode('utf-8'),
                                 content_type='application/json')

    def getCourier(self, courier_id):
        courier_url = reverse('modify_courier', args=[courier_id])
        return self.client.get(courier_url)

    def test_courier_json_good_one(self):
        response = self.modifyCourier(self.patch_json_good_one, 1)
        self.assertEquals(response.status_code, 200)

    def test_courier_json_good_one(self):
        response = self.modifyCourier(self.patch_json_good_two, 2)
        self.assertEquals(response.status_code, 200)

    def test_courier_json_invalid_value(self):
        response = self.modifyCourier(self.patch_json_invalid_value, 1)
        self.assertEquals(response.status_code, 400)

    def test_courier_json_invalid_field(self):
        response = self.modifyCourier(self.patch_json_invalid_field, 1)
        self.assertEquals(response.status_code, 400)

    def test_courier_json_plus_id_bad(self):
        response = self.modifyCourier(self.patch_json_plus_id_bad, 1)
        self.assertEquals(response.status_code, 400)

    def test_courier_json_get_good_one(self):
        response = self.getCourier(1)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, self.courier_one_inf)


class TestOrdersView(TestCase):
    orders_json_good = {'data': [
        {"order_id": 1, "weight": 0.23, "region": 12, "delivery_hours": ["11:30-15:00"]}]}
    orders_json_good_response = {"orders": [{"id": 1}]}
    orders_json_invalid_id = {'data': [
        {"order_id": 'text', "weight": 0.23, "region": 12, "delivery_hours": ["11:30-15:00"]}]}
    orders_json_missing_fields = {'data': [
        {"order_id": 5, "weight": 0.23, "delivery_hours": ["11:30-15:00"]}, \
        {"order_id": 11, "weight": 50, "region": 32, "delivery_hours": ["10:00-11:40", "16:00-18:00"]}]}
    orders_json_missing_fields_response = {
        "validation_error": {
            "orders": [{"id": 5}]}
    }
    orders_json_additional_fields = {'data': [
        {"order_id": 'text', 'temperature': 4, "weight": 0.23, "region": 12, "delivery_hours": ["11:30-15:00"]}]}
    orders_json_id_exists = {'data': [
        {"order_id": 4, "weight": 0.23, "region": 12, "delivery_hours": ["11:30-15:00"]}]}

    def setUp(self):
        self.client = Client()
        self.client.post(orders_url,
                         data=json.dumps(orders_json).encode('utf-8'),
                         content_type='application/json')

    def publishOrders(self, input_dict):
        return self.client.post(orders_url,
                                data=json.dumps(input_dict).encode('utf-8'),
                                content_type='application/json')

    def test_orders_good(self):
        response = self.publishOrders(self.orders_json_good)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(data, self.orders_json_good_response)

    def test_orders_invalid_id(self):
        response = self.publishOrders(self.orders_json_invalid_id)
        self.assertEquals(response.status_code, 400)

    def test_orders_missing_fields(self):
        response = self.publishOrders(self.orders_json_missing_fields)
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(data, self.orders_json_missing_fields_response)

    def test_orders_additional_fields(self):
        response = self.publishOrders(self.orders_json_additional_fields)
        self.assertEquals(response.status_code, 400)

    def test_orders_id_exists(self):
        response = self.publishOrders(self.orders_json_id_exists)
        self.assertEquals(response.status_code, 400)


class AssignOrdersView(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post(couriers_url,
                         data=json.dumps(couriers_json).encode('utf-8'),
                         content_type='application/json')
        self.client.post(orders_url,
                         data=json.dumps(orders_json).encode('utf-8'),
                         content_type='application/json')

    def assignOrders(self, courier_id):
        courier_dict = {
            "courier_id": courier_id
        }
        return self.client.post(assign_orders_url,
                                data=json.dumps(courier_dict).encode('utf-8'),
                                content_type='application/json')

    def test_assign_order_courier_one(self):
        response = self.assignOrders(1)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['orders'], [{'id': 5}])

    def test_assign_order_courier_two(self):
        response = self.assignOrders(2)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['orders'], [{'id': 12}, {'id': 35}, {'id': 39}, {'id': 40}])

    def test_assign_order_courier_id_not_exists(self):
        response = self.assignOrders(35)
        self.assertEquals(response.status_code, 400)


class CompleteOrderView(TestCase):
    complete_order_json_good = {
        "courier_id": 2,
        "order_id": 35,
        "complete_time": "2021-01-10T10:33:01.42Z"
    }
    complete_order_json_good_wrong_courier = {
        "courier_id": 1,
        "order_id": 35,
        "complete_time": "2021-01-10T10:33:01.42Z"
    }
    complete_order_json_one = {
        "courier_id": 1,
        "order_id": 5,
        "complete_time": (datetime.datetime.now() + datetime.timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')
    }

    def setUp(self):
        self.client = Client()
        self.client.post(couriers_url,
                         data=json.dumps(couriers_json).encode('utf-8'),
                         content_type='application/json')
        self.client.post(orders_url,
                         data=json.dumps(orders_json).encode('utf-8'),
                         content_type='application/json')

    def assignOrders(self, courier_id):
        courier_dict = {
            "courier_id": courier_id
        }
        return self.client.post(assign_orders_url,
                                data=json.dumps(courier_dict).encode('utf-8'),
                                content_type='application/json')

    def completeOrder(self, input_dict):
        return self.client.post(complete_order_url,
                                data=json.dumps(input_dict).encode('utf-8'),
                                content_type='application/json')

    def test_complete_order_courier_one(self):
        assign_response = self.assignOrders(courier_id=1)
        print('order assigned to courier 1:', json.loads(assign_response.content))
        response = self.completeOrder(self.complete_order_json_one)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['order_id'], 5)

    def test_complete_order_courier_two(self):
        self.assignOrders(courier_id=2)
        response = self.completeOrder(self.complete_order_json_good)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data['order_id'], 35)

    def test_complete_order_courier_one_wrong(self):
        self.assignOrders(courier_id=2)
        response = self.completeOrder(self.complete_order_json_good_wrong_courier)
        self.assertEquals(response.status_code, 400)


class TestCourierViewGet(TestCase):
    complete_order_json_one = {
        "courier_id": 1,
        "order_id": 5,
        "complete_time": '2021-05-10T21-09-27.42Z'
    }
    complete_order_json_three = {
        "courier_id": 3,
        "order_id": 4,
        "complete_time": "2021-05-10T21:45:01.42Z"
    }
    courier_json_one_inf = {"courier_id": 1, "courier_type": "foot", "regions": [5, 12, 22],
                            "working_hours": ["11:35-14:55"],
                            'earnings': 1000, 'rating': 4.17}

    def assignOrder(self, courier_id):
        courier_dict = {
            "courier_id": courier_id
        }
        return self.client.post(assign_orders_url,
                                data=json.dumps(courier_dict).encode('utf-8'),
                                content_type='application/json')

    def completeOrder(self, input_dict):
        return self.client.post(complete_order_url,
                                data=json.dumps(input_dict).encode('utf-8'),
                                content_type='application/json')

    def setUp(self):
        self.client = Client()
        self.client.post(couriers_url,
                         data=json.dumps(couriers_json).encode('utf-8'),
                         content_type='application/json')
        self.client.post(orders_url,
                         data=json.dumps(orders_json).encode('utf-8'),
                         content_type='application/json')
        response = self.assignOrder(1)
        data = json.loads(response.content)
        orders = data['orders']
        time_delta = datetime.timedelta(minutes=10)
        i = 1
        for order in orders:
            self.completeOrder({
                "courier_id": 1,
                "order_id": order['id'],
                "complete_time": (datetime.datetime.now() + time_delta * i).strftime('%Y-%m-%dT%H:%M:%S')
            })
            i += 1

    def couriers_GET(self, courier_id):
        courier_url = reverse('modify_courier', args=[courier_id])
        return self.client.get(courier_url)

    def test_courier_good_get(self):
        response = self.couriers_GET(1)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, self.courier_json_one_inf)
