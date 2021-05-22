from django.http import JsonResponse, HttpResponse
from .serializers import CourierSerializer, OrderSerializer, OrderCompleteSerializer, OrderAssignSerializer
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.views import View
from .models import CourierModel, OrderModel
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.db.models import Avg
from .utils import ResponseAfterValidation, courier_capacity_and_salary_coefficient, time_overlap


class CouriersView(View):
    def post(self, request):
        data = JSONParser().parse(request)
        serialized = CourierSerializer(data=data['data'], many=True)
        if serialized.is_valid():
            serialized.save()
            return JsonResponse(ResponseAfterValidation.imported_id(serialized, 'courier'),
                                status=status.HTTP_201_CREATED)
        return JsonResponse(ResponseAfterValidation.not_validated_id(serialized, 'courier'),
                            status=status.HTTP_400_BAD_REQUEST)


class CourierView(View):
    def withdraw_orders(self, courier_object):
        query_set = OrderModel.objects.filter(courier=courier_object.courier_id, complete_time=None)
        query_set_suitable = query_set.filter(region__in=courier_object.regions,
                                              weight__lte=
                                              courier_capacity_and_salary_coefficient(courier_object.courier_type)[
                                                  'capacity'])
        query_set_suitable_delivery_time = time_overlap(query_set_suitable, courier_object.working_hours)
        query_set_not_suitable = query_set.difference(query_set_suitable_delivery_time)
        for order in query_set_not_suitable:
            order.courier = None
            order.assign_time = None
            order.courier_capacity_and_salary_coefficient = None
            order.save()

    def get(self, request, courier_id):
        courier_object = get_object_or_404(CourierModel, courier_id=courier_id)
        serializer = CourierSerializer(courier_object)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, courier_id):
        courier_object = get_object_or_404(CourierModel, courier_id=courier_id)
        data = JSONParser().parse(request)
        serialized = CourierSerializer(courier_object, data=data, partial=True)
        if serialized.is_valid():
            try:
                serialized.save()
            except ValidationError:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            self.withdraw_orders(courier_object)
            courier_object = get_object_or_404(CourierModel, courier_id=courier_id)
            serializer = CourierSerializer(courier_object)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class OrdersView(View):
    def post(self, request):
        data = JSONParser().parse(request)
        serialized = OrderSerializer(data=data['data'], many=True)
        if serialized.is_valid():
            serialized.save()
            return JsonResponse(ResponseAfterValidation.imported_id(serialized, 'order'),
                                status=status.HTTP_201_CREATED)
        return JsonResponse(ResponseAfterValidation.not_validated_id(serialized, 'order'),
                            status=status.HTTP_400_BAD_REQUEST)


class AssignOrdersView(View):
    def assign_orders(self, courier_object):
        response = {
            'orders': [],
        }
        query_set = OrderModel.objects.filter(assign_time=None, region__in=courier_object.regions,
                                              weight__lte=
                                              courier_capacity_and_salary_coefficient(courier_object.courier_type)[
                                                  'capacity'])
        query_set_suitable_delivery_time = time_overlap(query_set, courier_object.working_hours)
        if query_set_suitable_delivery_time:
            response['assign_time'] = datetime.now()
            query_set_suitable_delivery_time.update(courier=courier_object, assign_time=response['assign_time'],
                                                    courier_salary_coefficient=courier_capacity_and_salary_coefficient(
                                                        courier_object.courier_type)['salary_coefficient'])
            for order in query_set_suitable_delivery_time:
                response['orders'].append({'id': order.order_id})
        return response

    def post(self, request):
        data = JSONParser().parse(request)
        serialized_data = OrderAssignSerializer(data=data)
        if serialized_data.is_valid:
            try:
                courier_object = CourierModel.objects.get(courier_id=int(data['courier_id']))
            except CourierModel.DoesNotExist:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            response = self.assign_orders(courier_object)
            return JsonResponse(response, status=status.HTTP_200_OK)
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class OrderCompleteView(View):
    def calculate_order_delivery_time(self, order_object):
        completed_orders = OrderModel.objects.filter(courier_id=order_object.courier_id, region=order_object.region) \
            .exclude(complete_time=None).order_by('-complete_time')
        if len(completed_orders) == 1:
            order_object.delivery_time = (order_object.complete_time - order_object.assign_time).total_seconds()
        else:
            order_object.delivery_time = (
                    order_object.complete_time - completed_orders[1].complete_time).total_seconds()
        order_object.save()
        return completed_orders

    def update_courier_data(self, courier_id, completed_orders, order_object):
        courier = CourierModel.objects.get(courier_id=courier_id)
        average_delivery_time = completed_orders.aggregate(Avg('delivery_time'))['delivery_time__avg']
        if courier.min_delivery_time is None or average_delivery_time < courier.min_delivery_time:
            courier.min_delivery_time = average_delivery_time
            courier.rating = round((60 * 60 - min(courier.min_delivery_time, 60 * 60)) / (60 * 60) * 5, 2)
        payment_for_order = 500 * order_object.courier_salary_coefficient
        courier.earnings += payment_for_order
        courier.save()

    def post(self, request):
        data = JSONParser().parse(request)
        serialized_data = OrderCompleteSerializer(data=data)
        if serialized_data.is_valid():
            try:
                order_object = OrderModel.objects.get(courier_id=data['courier_id'], order_id=data['order_id'],
                                                      complete_time=None)
            except OrderModel.DoesNotExist:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            order_object.complete_time = serialized_data.validated_data['complete_time']
            order_object.save()
            completed_orders = self.calculate_order_delivery_time(order_object)
            self.update_courier_data(data['courier_id'], completed_orders, order_object)
            return JsonResponse({'order_id': data['order_id']}, status=status.HTTP_200_OK)
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
