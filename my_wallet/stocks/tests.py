from django.test import TestCase
from .models import Stocks, Prices


class StocksModels(TestCase):
    def setUp(self):
        Stocks.get_stocks_with_data('AAPL')
        self.apple = Stocks.objects.get(ticker='AAPL')

    def test_creation_stocks(self):
        self.assertEquals(self.apple.ticker, 'AAPL')
        #self.assertContains(self.apple.name, 'Apple')

    def test_creation_prices(self):
        prices = Prices.objects.filter(stock=self.apple).count()
        self.assertTrue(prices>100)