from .models import OrderModel


class ResponseAfterValidation:

    def imported_id(serialized_list, model_object_name):
        imported_id = {model_object_name + 's': []}
        for data in serialized_list.validated_data:
            imported_id[model_object_name + 's'].append({"id": data[model_object_name + '_id']})
        return imported_id

    def not_validated_id(serialized_list, model_object_name):
        not_validated_id = {
            'validation_error':
                {
                    model_object_name + 's': []
                }
        }
        for data, error in zip(serialized_list.initial_data, serialized_list.errors):
            if error:
                not_validated_id['validation_error'][model_object_name + 's'].append(
                    {'id': data[model_object_name + '_id']})
        return not_validated_id


def courier_capacity_and_salary_coefficient(courier_type):
    if courier_type == 'foot':
        capacity = 10
        salary_coefficient = 2
    elif courier_type == 'bike':
        capacity = 15
        salary_coefficient = 5
    elif courier_type == 'car':
        capacity = 50
        salary_coefficient = 9
    return {'capacity': capacity, 'salary_coefficient': salary_coefficient}


def time_overlap(query_set, courier_working_hours):
    orders_set_suitable_working_intervals = []
    for working_hours_interval in courier_working_hours:
        for order_object in query_set:
            for delivery_hours_interval in order_object.delivery_hours:
                if working_hours_interval[0] <= delivery_hours_interval[1] \
                        and delivery_hours_interval[0] <= working_hours_interval[1]:
                    orders_set_suitable_working_intervals.append(order_object.order_id)
                    break
    return OrderModel.objects.filter(order_id__in=orders_set_suitable_working_intervals)
