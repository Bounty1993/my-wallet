from django.test import TestCase
from .models import *
import datetime


class MyModelTests(TestCase):

    def setUp(self):
        self.stock=Stocks.objects.create(name='Apple',
                              ticker='AAPL',
                              price=100.67,
                              date_price=datetime.datetime(2020, 5, 17))

    def test_get_past_data(self):
        self.stock.get_past_data()
        self.assertTrue(Stocks.objects.count() > 100)
