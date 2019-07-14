from django.test import TestCase
from django.urls import reverse
from unittest import mock
from django.utils.html import escape

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
        context = response.context

        expected_return = (110 * 5) / self.portfolio.total_value * 100
        self.assertEqual(context['data'][0][0], 'AAPL')
        self.assertEqual(context['data'][0][1], round(float(expected_return), 2))

        self.assertDictEqual(context['portfolio'], self.portfolio.get_summary())

        expected_assets = self.portfolio.asset.all().prefetch_related('stocks')
        self.assertEqual(context['assets'].first(), expected_assets.first())

    def test_portfolio_details_no_login(self):
        self.client.logout()
        url = reverse('portfolio:details', kwargs={'pk': self.portfolio.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_portfolio_details_not_owner(self):
        Profile.objects.create_user(username='Tester2', password='Tester123')
        self.client.login(username='Tester2', password='Tester123')
        url = reverse('portfolio:details', kwargs={'pk': self.portfolio.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @mock.patch('my_wallet.portfolio.views.Stocks.get_current_price')
    def test_transaction_buy_status_code(self, current_price):
        current_price.return_value = 120
        url = reverse('portfolio:transaction', kwargs={'pk': self.portfolio.id, 'kind': 'buy'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('my_wallet.portfolio.views.Stocks.get_current_price')
    def test_transaction_buy_post_valid(self, current_price):
        current_price.return_value = 120
        url = reverse('portfolio:transaction', kwargs={'pk': self.portfolio.id, 'kind': 'buy'})
        data = {'stocks': self.stocks.id, 'number': 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.number, 5)
        self.assertEqual(transaction.kind, 'buy')
        self.assertEqual(transaction.price, 120)

    @mock.patch('my_wallet.portfolio.views.Stocks.get_current_price')
    def test_transaction_buy_post_invalid(self, current_price):
        current_price.return_value = 120
        url = reverse('portfolio:transaction', kwargs={'pk': self.portfolio.id, 'kind': 'buy'})
        data = {'stocks': self.stocks.id, 'number': 10000}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        expected_error = escape('Środki finansowe są niewystarczające')
        self.assertContains(response, expected_error)

    @mock.patch('my_wallet.portfolio.views.Stocks.get_current_price')
    def test_transaction_sell_status_code(self, current_price):
        current_price.return_value = 120
        url = reverse('portfolio:transaction', kwargs={'pk': self.portfolio.id, 'kind': 'sell'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        actual_stocks = response.context['form'].fields['stocks'].queryset
        expected_stocks = self.profile.portfolio.first().asset.all()
        self.assertEqual(list(actual_stocks), list(expected_stocks))

    @mock.patch('my_wallet.portfolio.views.Stocks.get_current_price')
    def test_transaction_buy_sell_valid(self, current_price):
        current_price.return_value = 120
        url = reverse('portfolio:transaction', kwargs={'pk': self.portfolio.id, 'kind': 'sell'})
        data = {'stocks': self.stocks.id, 'number': 4}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.number, 4)
        self.assertEqual(transaction.kind, 'sell')
        self.assertEqual(transaction.price, 120)

    @mock.patch('my_wallet.portfolio.views.Stocks.get_current_price')
    def test_transaction_buy_sell_invalid(self, current_price):
        current_price.return_value = 120
        url = reverse('portfolio:transaction', kwargs={'pk': self.portfolio.id, 'kind': 'sell'})
        data = {'stocks': self.stocks.id, 'number': 10000}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        expected_error = escape('Nie możesz sprzedać więcej akcji niż posiadasz')
        self.assertContains(response, expected_error)

    def test_past_transactions(self):
        url = reverse('portfolio:past_transactions', kwargs={'pk': self.portfolio.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)