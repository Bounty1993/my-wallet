from django.test import Client, TestCase
from django.urls import reverse
from django.urls import resolve
from datetime import datetime

from ..models import Stocks, Dividends, Prices

from ..views import StocksListView


class StockListViewTest(TestCase):

    def test_status_code(self):
        url = reverse('stocks:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StockDetailViewTest(TestCase):
    def setUp(self):
        self.stock = Stocks.objects.create(
            name='APPLE',
            ticker='AAPL',
        )
        Dividends.objects.create(
            stock=self.stock,
            amount=100,
            record='2012-01-01',
            payment='2012-01-01'
        )

    def test_invalid_status_code(self):
        url = reverse('stocks:detail', kwargs={'ticker': 'BA'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_valid_status_code(self):
        url = reverse('stocks:detail', kwargs={'ticker': 'AAPL'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
