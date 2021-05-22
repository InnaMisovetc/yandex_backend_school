from django.test import TestCase
from django.urls import reverse, resolve

from delivery_service import views


class TestUrls(TestCase):
    def test_url_import_couriers_resolves(self):
        url = reverse('import_couriers')
        self.assertEquals(resolve(url).func.view_class, views.CouriersView)

    def test_url_modify_courier_resolves(self):
        url = reverse('modify_courier', args=[10])
        self.assertEquals(resolve(url).func.view_class, views.CourierView)

    def test_url_import_orders_resolves(self):
        url = reverse('import_orders')
        self.assertEquals(resolve(url).func.view_class, views.OrdersView)

    def test_url_assign_orders_resolves(self):
        url = reverse('assign_orders')
        self.assertEquals(resolve(url).func.view_class, views.AssignOrdersView)

    def test_url_complete_order_resolves(self):
        url = reverse('complete_order')
        self.assertEquals(resolve(url).func.view_class, views.OrderCompleteView)
