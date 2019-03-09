from django.test import TestCase
from .models import Stocks, Prices
from .utils import StockMaker


class StocksModels(TestCase):
    def setUp(self):
        StockMaker('AAPL').add_all()
        self.apple = Stocks.objects.get(ticker='AAPL')

    def test_creation_stocks(self):
        self.assertEquals(self.apple.ticker, 'AAPL')
        self.assertEquals(self.apple.name, 'Apple')

    def test_creation_prices(self):
        prices = Prices.objects.filter(stock=self.apple).count()
        self.assertTrue(prices>100)
