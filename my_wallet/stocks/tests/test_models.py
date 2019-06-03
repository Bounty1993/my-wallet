from datetime import date

from django.core.cache import cache
from django.test import Client, TestCase

from my_wallet.stocks.models import (
    Dividends, Financial, Prices, Stocks, find_quote_day,
)
from my_wallet.stocks.utils import StockMaker

"""
class StocksModels(TestCase):
    def setUp(self):
        Stocks.objects.create(
            ticker='AAPL',
            name='Apple Inc'
        )
        self.apple = Stocks.objects.get(ticker='AAPL')
        cache.set('AAPL_price', 100)
        cache.set('AAPL_day_change', 5)
        cache.set('AAPL_percent_change', 0.05)
        cache.set('AAPL_day_low', 95)
        cache.set('AAPL_day_high', 105)

    def test_creation_stocks(self):
        self.assertEquals(self.apple.ticker, 'AAPL')
        self.assertEquals(self.apple.name, 'Apple Inc')

    def test_price_properties(self):
        self.assertEquals(self.apple.current_price, 100)
        self.assertEquals(self.apple.day_change, 5)
        self.assertEquals(self.apple.percent_change, 0.05)
        self.assertEquals(self.apple.day_low, 95)
        self.assertEquals(self.apple.day_high, 105)


class DividendsTest(TestCase):
    def setUp(self):
        self.stock = Stocks.objects.create(
            ticker='AAPL',
            name='Apple'
        )
        data = [
            {'amount': 11, 'payment': date(2016, 3, 1), 'record': date(2016, 3, 2)},
            {'amount': 12, 'payment': date(2017, 3, 1), 'record': date(2017, 3, 2)},
            {'amount': 13, 'payment': date(2017, 6, 1), 'record': date(2017, 6, 2)},
            {'amount': 14, 'payment': date(2018, 6, 1), 'record': date(2018, 6, 2)},
        ]
        for line in data:
            Dividends.objects.create(
                stock=self.stock,
                amount=line['amount'],
                payment=line['payment'],
                record=line['record']
            )
        self.dividend = Dividends.objects.get(payment=date(2018, 6, 1))

    def test_init(self):
        self.assertEquals(Dividends.objects.count(), 4)

    def test_get_rate(self):
        price = Prices.objects.create(
            stock=self.stock,
            date_price=date(2018, 6, 2),
            price=100
        )
        rate = self.dividend.get_rate
        actual_rate = round((14/100) * 100)   # to make percent
        self.assertEquals(float(rate), actual_rate)

    def test_highest_rate(self):
        data = Stocks.highest_dividends()[0]
        self.assertEquals(data['sum_dividends'], 27)
        self.assertEquals(data['ticker'], 'AAPL')

    def test_dividend_amount(self):
        actual_amount = 27
        test_amount = self.stock.dividend_amount
        self.assertEquals(float(test_amount), actual_amount)

    def test_dividend_rate(self):
        actual_rate = 27 / 100
        test_rate = self.stock.dividend_rate
        test_rate = round(float(test_rate), 4)
        self.assertEquals(test_rate, actual_rate)


class FinancialTest(TestCase):

    def setUp(self):
        self.stock = Stocks.objects.get(
            ticker='AAPL',
            name='Apple Inc'
        )
        self.model = Financial.objects.create(
            stock=self.stock,
            assets=10_000,
            liabilities=5_000,
            total_revenue=10_000,
            gross_profit=1_000,
            operating_income=800,
            net_income=500,
        )

    def test_init(self):
        self.assertEquals(self.model.stock, self.stock)
        self.assertEquals(self.model.assets, 10_000)
        self.assertEquals(self.model.liabilities, 5_000)
        self.assertEquals(self.model.total_revenue, 10_000)
        self.assertEquals(self.model.gross_profit, 1_000)
        self.assertEquals(self.model.operating_income, 800)
        self.assertEquals(self.model.net_income, 500)

    def test_equity(self):
        self.assertEquals(self.model.equity, 5_000)

    def test_operating_margin(self):
        self.assertEquals(self.model.operating_margin, 0.08)

    def test_net_margin(self):
        self.assertEquals(self.model.net_margin, 0.05)
"""