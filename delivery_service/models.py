from django.db import models
from django.contrib.postgres.fields import ArrayField

TYPE_CHOICES = [('foot', 'foot'), ('bike', 'bike'), ('car', 'car')]


class CourierModel(models.Model):
    courier_id = models.IntegerField(unique=True, primary_key=True)
    courier_type = models.CharField(choices=TYPE_CHOICES, max_length=5)
    regions = ArrayField(models.PositiveIntegerField())
    working_hours = ArrayField(ArrayField(models.TimeField()))
    rating = models.FloatField(null=True)
    earnings = models.IntegerField(default=0)
    min_delivery_time = models.FloatField(null=True)


class OrderModel(models.Model):
    order_id = models.IntegerField(unique=True, primary_key=True)
    weight = models.FloatField()
    region = models.IntegerField()
    delivery_hours = ArrayField(ArrayField(models.TimeField()))
    courier = models.ForeignKey(CourierModel, on_delete=models.SET_NULL, null=True)
    courier_salary_coefficient = models.IntegerField(null=True)
    assign_time = models.DateTimeField(null=True)
    complete_time = models.DateTimeField(null=True)
    delivery_time = models.IntegerField(null=True)
