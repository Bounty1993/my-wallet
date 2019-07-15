from django.test import TestCase
from unittest import mock

from my_wallet.portfolio.tasks import price_update, update_portfolio_history
from my_wallet.stocks.models import Stocks


class TasksTest(TestCase):
    @mock.patch('my_wallet.portfolio.tasks.cache')
    @mock.patch('my_wallet.portfolio.tasks.QuotesIEX.get_data')
    def test_price_update(self, mock_quotes, mock_cache):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        data = {
            'latestPrice': 100, 'change': 10,
            'changePercent': -0.01, 'low': None,
            'high': 110
        }
        options = {}
        mock_quotes.return_value.get = lambda key, default: data.get(key) or default
        mock_cache.set = lambda key, value: options.update({key: value})
        price_update()
        expected = {
            'AAPL_price': 100, 'AAPL_day_change': 10,
            'AAPL_percent_change': -1, 'AAPL_day_low': 'no data',
            'AAPL_day_high': 110
        }
        self.assertDictEqual(options, expected)

    def test_update_portfolio_history(self):
        pass