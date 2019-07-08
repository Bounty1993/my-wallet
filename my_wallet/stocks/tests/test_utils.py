from datetime import datetime

from django.test import TestCase
from unittest import mock

from my_wallet.stocks.utils import StockMaker
from my_wallet.stocks.models import Stocks, StockDetail, Dividends, Financial, Prices


class StockMakerTest(TestCase):

    @mock.patch('my_wallet.stocks.utils.QuotesIEX.get_data')
    def test_add_stocks(self, mock_data):
        mock_data.return_value = {
            'companyName': 'Apple',
            'symbol': 'AAPL',
        }
        StockMaker('AAPL').add_stocks()
        stock = Stocks.objects.first()
        self.assertEqual(stock.ticker, 'AAPL')
        self.assertEqual(stock.name, 'Apple')

    @mock.patch('my_wallet.stocks.utils.CompanyIEX.get_data')
    def test_add_detail(self, mock_data):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        mock_data.return_value = {
            'sector': 'Technology',
            'industry': 'IT',
            'website': 'www.apple.com',
            'description': 'Best company ever',
        }
        StockMaker('AAPL').add_detail()
        detail = StockDetail.objects.first()
        self.assertEqual(detail.stock.ticker, 'AAPL')
        self.assertEqual(detail.sector, 'Technology')
        self.assertEqual(detail.website, 'www.apple.com')

    @mock.patch('my_wallet.stocks.utils.DividendsIEX.get_data')
    def test_add_dividends(self, mock_data):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        mock_data.return_value = [{
            'paymentDate': '2019-01-01',
            'recordDate': '2018-12-11',
            'amount': 110.0
        }]
        StockMaker('AAPL').add_dividends()
        dividends = Dividends.objects.first()
        self.assertEqual(dividends.stock.ticker, 'AAPL')
        self.assertEqual(dividends.record, datetime(2018, 12, 11).date())
        self.assertEqual(dividends.amount, 110)

    @mock.patch('my_wallet.stocks.utils.FinancialIEX.get_data')
    def test_add_financial(self, mock_data):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        mock_data.return_value = [{
            'totalAssets': 1_000_000, 'totalLiabilities': 500_000,
            'totalRevenue': 1_000_000, 'grossProfit': 100_000,
            'operatingIncome': 80_000, 'netIncome': 50_000,
        }]
        StockMaker('AAPL').add_financial()
        financial = Financial.objects.first()
        self.assertEqual(financial.stock.ticker, 'AAPL')
        self.assertEqual(financial.assets, 1_000_000)
        self.assertEqual(financial.net_income, 50_000)

    @mock.patch('my_wallet.stocks.utils.PastIEX.get_data')
    def test_add_past_data(self, mock_data):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        mock_data.return_value = [{
            'close': 100,
            'date': '2019-01-01',
            'open': 109,
            'volume': 100_000,
            'change': 1,
            'changePercent': 1,
        }]
        StockMaker('AAPL').add_past_data()
        prices = Prices.objects.first()
        self.assertEqual(prices.stock.ticker, 'AAPL')
        self.assertEqual(prices.price, 100)
        self.assertEqual(prices.date_price, datetime(2019, 1, 1).date())
