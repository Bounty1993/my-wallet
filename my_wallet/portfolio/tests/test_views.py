from django.test import TestCase
from django.urls import reverse
from unittest import mock

from my_wallet.portfolio.models import Portfolio, Asset, Transaction
from my_wallet.stocks.models import Stocks
from my_wallet.profiles.models import Profile


class PortfolioViewTests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create_user(
            username='Tester', password='Tester123')
        self.portfolio = Portfolio.objects.create(
            name='Test Portfolio', profile=self.profile,
            beginning_cash=10000, cash=1000)
        self.stocks = Stocks.objects.create(name='Apple', ticker='AAPL')
        Asset.objects.create(
            portfolio=self.portfolio, stocks=self.stocks,
            avg_cost=100, sum_number=5)
        Transaction.objects.create(
            portfolio=self.portfolio, stocks=self.stocks,
            price=100, number=5, kind='buy')
        self.client.login(username='Tester', password='Tester123')

    def test_new_portofolio_no_login(self):
        self.client.logout()
        url = reverse('portfolio:new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_new_porfolio_status_code_correct(self):
        url = reverse('portfolio:new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_portfolio_post_valid(self):
        url = reverse('portfolio:new')
        data = {
            'name': 'Testowy',
            'description': 'Testowy opis',
            'beginning_cash': 10000,
            'is_visible': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    @mock.patch('my_wallet.stocks.models.cache')
    def test_portfolio_details(self, price_cache):
        price_cache.get.return_value = 110
        url = reverse('portfolio:details', kwargs={'pk': self.portfolio.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
