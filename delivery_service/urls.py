from django.urls import path
from . import views


urlpatterns = [
    path('couriers', views.CouriersView.as_view(), name='import_couriers'),
    path('couriers/<int:courier_id>', views.CourierView.as_view(), name='modify_courier'),
    path('orders', views.OrdersView.as_view(), name='import_orders'),
    path('orders/assign', views.AssignOrdersView.as_view(), name='assign_orders'),
    path('orders/complete', views.OrderCompleteView.as_view(), name='complete_order')]
