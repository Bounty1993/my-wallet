from django.test import TestCase
from .models import *
import datetime
from my_wallet.profiles.models import Profile
from .models import Portfolio, Transaction
from my_wallet.stocks.models import Stocks

class MyModelTests(TestCase):

    def setUp(self):
        profile = Profile.objects.create_user(
            username='tester',
            password='123',
            email='tom@example.com'
        )

        self.portfolio = Portfolio.objects.create(
            name='testportfolio',
            profile=profile,
            beginning_cash=10000.00,
            current_cash=10000.00,
        )

        self.stocks = Stocks.objects.create(name='Apple', ticker='AAPL')

        self.stock_price = Stocks.get_current_price('AAPL')

    def test_buy_transaction(self):
        self.portfolio.make_transaction('AAPL', 200, 'B')
        cash = self.portfolio.current_cash
        self.assertTrue(cash < 10000)

    def test_portfolio_buy_asset_creation_asset(self):
        self.portfolio.make_transaction('AAPL', 200, 'B')
        asset = Asset.objects.all().first()
        self.assertEqual(asset.portfolio, self.portfolio)
        self.assertEqual(asset.stocks, self.stocks)
        self.assertEquals(asset.avg_cost, self.stock_price)
        self.assertEquals(asset.sum_number, 200)

    def test_portfolio_create_transaction(self):
        transaction = self.portfolio.create_transaction('AAPL', 200, 21.5)
        self.assertEqual(transaction.stocks, self.stocks)
        self.assertEqual(transaction.number, 200)
        self.assertEqual(transaction.price, 21.5)
        self.assertEqual(transaction.kind, 'B')
