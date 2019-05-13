from django.test import TestCase

from my_wallet.portfolio.models import Asset, Portfolio, Transaction
from my_wallet.profiles.models import Profile
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


    def test_buy(self):
        pass
