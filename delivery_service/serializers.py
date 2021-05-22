from rest_framework import serializers
from .models import CourierModel, OrderModel, TYPE_CHOICES
from datetime import datetime
from rest_framework.fields import empty
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueValidator


class CourierSerializer(serializers.ModelSerializer):

    courier_id = serializers.IntegerField(min_value=1,
                                          validators=[UniqueValidator(queryset=CourierModel.objects.all())])
    courier_type = serializers.ChoiceField(choices=TYPE_CHOICES)
    regions = serializers.ListField(child=serializers.IntegerField(min_value=1))
    working_hours = serializers.ListField()

    class Meta:
        model = CourierModel
        exclude = ('min_delivery_time',)

    def run_validation(self, data):
        required_fields = ('courier_id', 'courier_type', 'regions', 'working_hours')
        unknown = set(data) - set(required_fields)
        if unknown:
            errors = ["Unknown field: {}".format(f) for f in unknown]
            raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(CourierSerializer, self).run_validation(data)

    def update(self, instance, validated_data):
        if 'courier_id' in validated_data:
            raise serializers.ValidationError({
                'courier_id': 'You must not change this field.',
            })

        return super().update(instance, validated_data)

    def validate_working_hours(self, value):
        working_hours_list = []
        for time_range in value:
            try:
                time_range_list = time_range.split('-')
                working_hours_list.append([datetime.strptime(x, '%H:%M').time() for x in time_range_list])
            except:
                raise serializers.ValidationError('Enter valid working hours intervals')
        return working_hours_list

    def working_hours_representation(self, value):
        working_hours_list = []
        for time_range in value:
            time_range = [x.strftime('%H:%M') for x in time_range]
            time_range_joined = '-'.join(time_range)
            working_hours_list.append(time_range_joined)
        return working_hours_list

    def to_representation(self, instance):
        fields_to_be_removed = ('rating', 'earnings')
        rep = super().to_representation(instance)
        for field in fields_to_be_removed:
            try:
                if rep[field] is None:  # checks if value is 'None', this is different from "emptiness"
                    rep.pop(field)
            except KeyError:
                pass
        rep['working_hours'] = self.working_hours_representation(instance.working_hours)
        return rep


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(min_value=1, validators=[UniqueValidator(queryset=OrderModel.objects.all())])
    region = serializers.IntegerField(min_value=1)
    delivery_hours = serializers.ListField()

    class Meta:
        model = OrderModel
        exclude = ('courier', 'assign_time', 'complete_time', 'delivery_time', 'courier_salary_coefficient')

    def run_validation(self, data):
        unknown = set(data) - set(self.fields)
        if unknown:
            errors = ["Unknown field: {}".format(f) for f in unknown]
            raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(OrderSerializer, self).run_validation(data)

    def validate_weight(self, value):
        if value < 0.01 or value > 50:
            raise serializers.ValidationError('Weight should be more than 0.01 and less than 50')
        return round(value, 2)

    def validate_delivery_hours(self, value):
        working_hours_list = []
        for time_range in value:
            try:
                time_range_list = time_range.split('-')
                working_hours_list.append([datetime.strptime(x, '%H:%M').time() for x in time_range_list])
            except:
                raise serializers.ValidationError('Enter valid working hours intervals')
        return working_hours_list


class OrderAssignSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField(min_value=1)

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = ["Unknown field: {}".format(f) for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(OrderAssignSerializer, self).run_validation(data)


class OrderCompleteSerializer(OrderAssignSerializer):
    order_id = serializers.IntegerField(min_value=1)
    complete_time = serializers.DateTimeField()
