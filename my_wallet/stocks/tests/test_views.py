import csv
import io

from django.test import Client, TestCase
from django.urls import reverse
from datetime import datetime
from django.views.generic import TemplateView
from unittest import mock

from ..models import Stocks, Dividends, Prices, Financial
from my_wallet.stocks.views import (
    SideBarMixin, FinancialChartMixin, PriceChartMixin)


class DownloadPricesTest(TestCase):
    def setUp(self):
        self.stock = Stocks.objects.create(name='Apple', ticker='AAPL')
        self.price = Prices.objects.create(
            stock=self.stock, price=101, open=100,
            volume=100_000, change=1, percent_change=1,
            date_price=datetime(2019, 1, 1).date())

    def test_valid_csv_view(self):
        url = reverse('stocks:download_csv', kwargs={'ticker': 'AAPL'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)
        expected = [
            'date_price', 'price', 'open',
            'volume', 'change', 'percent_change'
        ]
        self.assertListEqual(headers, expected)
        expected = [
            '2019-01-01', '101.00', '100.00',
            '100000', '1.0', '1.0',
        ]
        self.assertListEqual(body[0], expected)

    def test_invalid_csv_view(self):
        url = reverse('stocks:download_csv', kwargs={'ticker': 'unknown'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_valid_excel_view(self):
        url = reverse('stocks:download_xml', kwargs={'ticker': 'AAPL'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # sprawdz response

    def test_invalid_excel_view(self):
        url = reverse('stocks:download_xml', kwargs={'ticker': 'unknown'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class StocksViewMixinsTest(TestCase):

    class DummyView(SideBarMixin, TemplateView):
            pass

    @mock.patch('my_wallet.stocks.views.cache')
    def test_side_bar_mixin(self, mock_cache):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        options = {
            'AAPL_price': 100,
            'AAPL_day_change': 10,
            'AAPL_percent_change': -10
        }
        mock_cache.get = lambda key, default: options[key]

        dummy_view = self.DummyView()
        dummy_view.kwargs = {'ticker': 'AAPL'}
        context = dummy_view.get_context_data()
        self.assertEqual(context['stocks_price'], 100)
        self.assertEqual(context['stocks_day_change'], 10)
        self.assertEqual(context['stocks_percent_change'], -10)
        self.assertEqual(context['side_stock'], 'Apple')

    class FinancialMixinDummyView(FinancialChartMixin, TemplateView):
        pass

    def test_financial_chart_mixin(self):
        stock = Stocks.objects.create(name='Apple', ticker='AAPL')
        financial = Financial.objects.create(
            stock=stock, assets=1_000_000, liabilities=500_000,
            total_revenue=1_000_000, gross_profit=100_000,
            operating_income=80_000, net_income=50_000)
        dummy_view = self.FinancialMixinDummyView()
        dummy_view.kwargs = {'ticker': 'AAPL'}
        context = dummy_view.get_context_data()
        self.assertTrue('finance_data' in context)
        self.assertTrue('balance_data' in context)

        finance_data_expected = [
            {'name': 'total_revenue', 'data': [1, ]},
            {'name': 'gross_profit', 'data': [0.1, ]},
            {'name': 'operating_income', 'data': [0.08, ]},
            {'name': 'net_income', 'data': [0.05, ]},
        ]
        self.assertListEqual(context['finance_data'], finance_data_expected)

        balance_data_expected = [
            {'name': 'assets', 'data': [1, ]},
            {'name': 'liabilities', 'data': [0.5, ]},
        ]
        self.assertListEqual(context['balance_data'], balance_data_expected)

    class PriceChartMixinDummyView(PriceChartMixin, TemplateView):
        pass

    def test_price_chart_mixin(self):
        stock = Stocks.objects.create(name='Apple', ticker='AAPL')
        Prices.objects.create(
            stock=stock, price=101, open=100,
            volume=100_000, change=1, percent_change=1,
            date_price=datetime(2019, 1, 1).date())
        Prices.objects.create(
            stock=stock, price=110, open=108,
            volume=100_000, change=2, percent_change=2,
            date_price=datetime(2019, 1, 2).date())

        dummy_view = self.PriceChartMixinDummyView()
        dummy_view.object_list = Prices.objects.filter(stock=stock)
        context = dummy_view.get_context_data()

        expected = {
            'name': 'Apple',
            'prices': [(1546300800000, 101.0), (1546387200000, 110.0)],
        }
        self.assertDictEqual(context['price_data'], expected)


class StockListViewTest(TestCase):

    def test_status_code(self):
        url = reverse('stocks:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StockDetailViewTest(TestCase):
    def setUp(self):
        self.stock = Stocks.objects.create(
            name='APPLE',
            ticker='AAPL',
        )
        Dividends.objects.create(
            stock=self.stock,
            amount=100,
            record='2012-01-01',
            payment='2012-01-01'
        )

    def test_invalid_status_code(self):
        url = reverse('stocks:detail', kwargs={'ticker': 'BA'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_valid_status_code(self):
        url = reverse('stocks:detail', kwargs={'ticker': 'AAPL'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ArticleViewTest(TestCase):

    @mock.patch('my_wallet.stocks.views.YahooCrawler.get_data')
    @mock.patch('my_wallet.stocks.views.GoogleCrawler.get_data')
    def test_status_code(self, mock_google, mock_yahoo):
        Stocks.objects.create(name='Apple', ticker='AAPL')
        mock_google.return_value = 'Hi there. I am Google Crawler'
        mock_yahoo.return_value = 'Hi there. I am YahooCrawler'

        url = reverse('stocks:articles', kwargs={'ticker': 'AAPL'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['google_news'], 'Hi there. I am Google Crawler')
        self.assertEqual(response.context['yahoo_news'], 'Hi there. I am YahooCrawler')
