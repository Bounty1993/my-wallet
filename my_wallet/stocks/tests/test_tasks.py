from datetime import datetime

from django.test import TestCase
from unittest import mock

from my_wallet.stocks.tasks import update_stock_price
from my_wallet.stocks.models import Stocks, Prices


class TasksTest(TestCase):
    def setUp(self):
        self.data = {
            'symbol': 'AAPL',
            'close': 120,
            'date': '2019-10-10',
            'open': 119.5,
            'volume': 10000,
            'change': 0.05,
            'changePercent': 0.01
        }

    @mock.patch('my_wallet.stocks.tasks.requests')
    def test_stock_update(self, mock_request):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        mock_request.get.return_value.status_code = 200
        mock_request.get.return_value.json.return_value = self.data
        update_stock_price()
        self.assertEqual(Prices.objects.count(), 1)
        apple = Prices.objects.get(stock__ticker='AAPL')
        self.assertEqual(apple.stock, Stocks.objects.first())
        self.assertEqual(apple.price, self.data['close'])
        self.assertEqual(apple.date_price, datetime(2019, 10, 10).date())

    @mock.patch('my_wallet.stocks.tasks.requests')
    def test_stock_no_data(self, mock_request):
        Stocks.objects.create(name='Amazon', ticker='AMZN')
        mock_request.get.return_value.status_code = 404
        mock_request.get.return_value.json.return_value = self.data
        update_stock_price()
        prices = Prices.objects.filter(stock__ticker='AMZN')
        self.assertTrue(prices.exists())
        amazon = prices.first()
        self.assertEqual(amazon.price, None)
        self.assertTrue(amazon.date_price, datetime.now().date())
