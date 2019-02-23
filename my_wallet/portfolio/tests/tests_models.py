from django.test import TestCase
from my_wallet.profiles.models import Profile
from my_wallet.portfolio.models import Portfolio, Transaction, Asset
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
            cash=10000.00,
        )

        self.stocks = Stocks.objects.create(name='Apple', ticker='AAPL')

        self.stock_price = Stocks.get_current_price('AAPL')

    def test_buy_transaction(self):
        self.portfolio.buy_transaction('AAPL', 20)
        cash = self.portfolio.cash
        self.assertTrue(cash < 10000)

    def test_portfolio_buy_asset_creation_asset(self):
        self.portfolio.buy_transaction('AAPL', 20)
        asset = Asset.objects.all().first()
        self.assertEqual(asset.portfolio, self.portfolio)
        self.assertEqual(asset.stocks, self.stocks)
        self.assertEquals(float(asset.avg_cost), self.stock_price)
        self.assertEquals(asset.sum_number, 20)

    def test_portfolio_create_transaction(self):
        transaction = self.portfolio.create_transaction('AAPL', 20, 21.5, 'B')
        self.assertEqual(transaction.stocks, self.stocks)
        self.assertEqual(transaction.number, 20)
        self.assertEqual(transaction.price, 21.5)
        self.assertEqual(transaction.kind, 'B')

    def test_buy_not_enough_money(self):
        with self.assertRaises(ValueError):
            self.portfolio.buy_transaction('AAPL', 200)
