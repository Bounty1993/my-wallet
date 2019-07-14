from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from unittest import mock

from my_wallet.portfolio.models import Asset, Portfolio, Transaction, PastPortfolio
from my_wallet.profiles.models import Profile
from my_wallet.stocks.models import Stocks


class PortfolioModelTest(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create_user(
            username='Tester', password='Tester123')
        self.portfolio = Portfolio.objects.create(
            name='Test Portfolio', profile=self.profile,
            beginning_cash=10000, cash=1000)
        self.apple = Stocks.objects.create(name='Apple', ticker='AAPL')
        Asset.objects.create(
            portfolio=self.portfolio, stocks=self.apple,
            avg_cost=100, sum_number=5)
        Transaction.objects.create(
            portfolio=self.portfolio, stocks=self.apple,
            price=100, number=5, kind='buy')
        self.amazon = Stocks.objects.create(name='Amazon', ticker='AMZN')
        Asset.objects.create(
            portfolio=self.portfolio, stocks=self.amazon,
            avg_cost=76, sum_number=10)
        Transaction.objects.create(
            portfolio=self.portfolio, stocks=self.amazon,
            price=76, number=10, kind='buy')
        self.client.login(username='Tester', password='Tester123')

    def test_str(self):
        self.assertEqual(self.portfolio.__str__(), 'Test Portfolio')

    @mock.patch('my_wallet.stocks.models.cache')
    def test_stocks_and_total_value(self, price_cache):
        price_cache.get.return_value = 120
        expected = 120 * 5 + 120 * 10
        self.assertEqual(self.portfolio.stocks_value, expected)
        expected = expected + self.portfolio.cash
        self.assertEqual(self.portfolio.total_value, expected)

    @mock.patch('my_wallet.stocks.models.cache')
    def test_get_summary(self, price_cache):
        price_cache.get.return_value = 120
        expected = {
            'stocks_value': 1800, 'total_value': Decimal('2800'),
            'total_return': Decimal('-7200'),
            'percent_return': Decimal('-72.00'), 'pk': self.portfolio.id,
            'beginning_cash': 10000, 'cash': 1000
        }
        self.assertDictEqual(self.portfolio.get_summary(), expected)

    def test_buy_already_has(self):
        initial_cach = self.portfolio.cash
        asset = self.portfolio.asset.get(stocks=self.apple)
        initial_number = asset.sum_number
        self.portfolio.buy(10, self.apple, 120)
        expected_cash = initial_cach - 1200
        self.assertEqual(self.portfolio.cash, expected_cash)
        asset = self.portfolio.asset.get(stocks=self.apple)
        expected_number = initial_number + 10
        self.assertEqual(asset.sum_number, expected_number)
        expected_avg_cost = 113.33
        self.assertEqual(float(asset.avg_cost), expected_avg_cost)

    def test_buy_new(self):
        initial_cash = self.portfolio.cash
        google = Stocks.objects.create(name='Google', ticker='GOOGL')
        self.portfolio.buy(10, google, 120)
        expected_cash = initial_cash - 1200
        self.assertEqual(self.portfolio.cash, expected_cash)
        asset = self.portfolio.asset.filter(stocks=google)
        self.assertTrue(asset.exists())
        self.assertEqual(asset.first().total_cost, 1200)
        self.assertEqual(asset.first().sum_number, 10)
        # self.assertEqual(asset.first().date.date(), datetime.now().date())

    def test_sell(self):
        initial_cash = self.portfolio.cash
        asset = self.portfolio.asset.get(stocks=self.apple)
        initial_number = asset.sum_number
        self.portfolio.sell(3, self.apple, 120)
        expected_cash = initial_cash + (120 * 3)
        self.assertEqual(self.portfolio.cash, expected_cash)
        asset = self.portfolio.asset.get(stocks=self.apple)
        expected_number = initial_number - 3
        self.assertEqual(asset.sum_number, expected_number)
        expected_avg_cost = 70
        self.assertEqual(float(asset.avg_cost), expected_avg_cost)

    def test_sell_to_zero(self):
        initial_cash = self.portfolio.cash
        self.portfolio.sell(5, self.apple, 120)
        expected_cash = initial_cash + (120 * 5)
        self.assertEqual(self.portfolio.cash, expected_cash)
        asset = self.portfolio.asset.filter(stocks=self.apple)
        self.assertFalse(asset.exists())

    """
    def test_has_transaction(self):
        self.assertTrue(self.portfolio.has_transactions())
    """

    @mock.patch('my_wallet.stocks.models.cache')
    def test_make_past_portfolio(self, price_cash):
        price_cash.get.return_value = 120
        self.portfolio.make_past_portfolio()
        past_portfolio = PastPortfolio.objects.filter(portfolio=self.portfolio)
        self.assertTrue(past_portfolio.exists())
