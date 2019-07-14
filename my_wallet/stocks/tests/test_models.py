from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.core.cache import cache

from django.test import Client, TestCase, override_settings

from my_wallet.stocks.models import (
    Dividends, Financial, Prices, Stocks, find_quote_day
)
from unittest import mock

percents = Decimal('0.0001')


class StocksModelsTest(TestCase):
    def setUp(self):
        self.apple = Stocks.objects.create(
            name='Apple', ticker='AAPL')
        self.price1 = Prices.objects.create(
            stock=self.apple, price=101, open=100,
            volume=100_000, change=1, percent_change=1,
            date_price=datetime(2019, 1, 1).date())
        self.price2 = Prices.objects.create(
            stock=self.apple, price=102, open=101,
            volume=100_000, change=1, percent_change=1,
            date_price=datetime(2019, 1, 2).date())
        self.price3 = Prices.objects.create(
            stock=self.apple, price=104, open=102,
            volume=100_000, change=2, percent_change=2,
            date_price=datetime(2019, 1, 3).date())

        self.price4 = Prices.objects.create(
            stock=self.apple, price=101, open=100,
            volume=100_000, change=1, percent_change=1,
            date_price=datetime(2017, 12, 31).date())

        self.financial = Financial.objects.create(
            stock=self.apple, assets=1_000_000, liabilities=500_000,
            total_revenue=1_000_000, gross_profit=100_000,
            operating_income=80_000, net_income=50_000)

        self.dividend = Dividends.objects.create(
            stock=self.apple, payment=datetime(2019, 2, 1).date(),
            record=datetime(2019, 1, 1).date(), amount=5)

        self.dividend1 = Dividends.objects.create(
            stock=self.apple, payment=datetime(2019, 2, 13).date(),
            record=datetime(2019, 1, 12).date(), amount=10)

        self.dividend3 = Dividends.objects.create(
            stock=self.apple, payment=datetime(2018, 12, 13).date(),
            record=datetime(2018, 12, 11).date(), amount=10)

    def test_find_quote_day(self):
        date = datetime(2019, 7, 7)  # Saturday
        actual = find_quote_day(date, days_ago=365)
        expected = datetime(2018, 7, 6)  # Friday
        self.assertEqual(actual, expected)

        date = datetime(2019, 7, 8)  # Sunday
        actual = find_quote_day(date, days_ago=365)
        expected = datetime(2018, 7, 6)  # Friday
        self.assertEqual(actual, expected)

        date = datetime(2019, 7, 9)  # Monday
        actual = find_quote_day(date, days_ago=365)
        expected = datetime(2018, 7, 6)  # Friday
        self.assertEqual(actual, expected)

        date = datetime(2019, 7, 6)  # Friday
        actual = find_quote_day(date, days_ago=365, type='later')
        expected = datetime(2018, 7, 9)  # Monday
        self.assertEqual(actual, expected)

        date = datetime(2019, 7, 7)  # Saturday
        actual = find_quote_day(date, days_ago=365, type='later')
        expected = datetime(2018, 7, 9)  # Monday
        self.assertEqual(actual, expected)

        date = datetime(2019, 7, 8)  # Sunday
        actual = find_quote_day(date, days_ago=365, type='later')
        expected = datetime(2018, 7, 9)  # Monday
        self.assertEqual(actual, expected)

    @mock.patch('my_wallet.stocks.models.datetime')
    @mock.patch('my_wallet.stocks.models.cache')
    def test_stocks_manager_highest_dividends(self, mock_cache, mock_datetime):
        mock_datetime.date.today.return_value = datetime(2018, 7, 6)
        mock_datetime.timedelta.return_value = timedelta(days=1)

        current_price = 100
        mock_cache.get.return_value = current_price

        expected = [{
            'ticker': self.apple.ticker,
            'sum_dividends': Decimal(25/current_price * 100)
        }]
        actual = Stocks.objects.highest_dividends()
        self.assertEqual(actual, expected)

    def test_stocks_str(self):
        self.assertEqual(self.apple.__str__(), 'Apple')

    @mock.patch('my_wallet.stocks.models.cache')
    def test_stocks_properties(self, mock_cache):
        options = {
            'AAPL_price': 100, 'AAPL_day_change': 10,
            'AAPL_percent_change': -10, 'AAPL_day_low': 90,
            'AAPL_day_high': 110
        }
        mock_cache.get = lambda key: options[key]

        self.assertEqual(self.apple.current_price, options['AAPL_price'])
        self.assertEqual(self.apple.day_change, options['AAPL_day_change'])
        self.assertEqual(self.apple.percent_change, options['AAPL_percent_change'])
        self.assertEqual(self.apple.day_low, options['AAPL_day_low'])
        self.assertEqual(self.apple.day_high, options['AAPL_day_high'])

    @mock.patch('my_wallet.stocks.models.datetime')
    def test_stocks_dividend_amount(self, mock_datetime):
        mock_datetime.date.today.return_value = datetime(2018, 12, 31)
        mock_datetime.timedelta.return_value = timedelta(days=1)
        actual = self.apple.dividend_amount()
        expected = self.dividend.amount + self.dividend1.amount
        self.assertEqual(actual, expected)

    @mock.patch('my_wallet.stocks.models.timezone')
    def test_stocks_find_past_price(self, mock_timezone):
        mock_timezone.now().date.return_value = datetime(2019, 7, 6).date()
        expected = Prices.objects.create(
            stock=self.apple, price=101, open=100,
            volume=100_000, change=1, percent_change=1,
            date_price=datetime(2018, 5, 6).date())
        actual = self.apple.find_past_price(365)
        self.assertEqual(actual, expected.price)

    def test_stocks_dividend_summarize(self):
        dividend = self.apple.dividends.first()
        first_element = {
            'payment': dividend.payment,
            'record': dividend.record,
            'amount': dividend.amount,
            'quarter': dividend.which_quarter()
        }
        actual = self.apple.dividends_summarize()
        self.assertDictEqual(actual[0], first_element)

    def test_stocks_dividend_summarize_empty(self):
        self.apple = Stocks.objects.create(
            name='Google', ticker='GOOGL')
        actual = self.apple.dividends_summarize()
        expected = []
        self.assertListEqual(actual, expected)

    @mock.patch('my_wallet.stocks.models.datetime')
    @mock.patch('my_wallet.stocks.models.timezone')
    def test_stocks_get_change(self, mock_timezone, mock_datetime):
        mock_timezone.now.return_value.date.return_value = datetime(2019, 6, 6)
        mock_datetime.timedelta.return_value = timedelta(days=365)
        actual = self.apple.get_change(num_days=356)
        expected_currency = 101 - 104
        self.assertEqual(actual['currency'], expected_currency)
        expected_percent = (101 / 104 - 1) * 100
        self.assertAlmostEqual(actual['percent'], Decimal(expected_percent))

    def test_stocks_get_change_no_data(self):
        amazon = Stocks.objects.create(name='Amazon', ticker='AMZN')
        expected = {'currency': 'No data', 'percent': 'no data'}
        self.assertEqual(amazon.get_change(365), expected)

    def test_prices_order(self):
        actual = Prices.objects.all()
        expected = [self.price3, self.price2, self.price1, self.price4]
        self.assertEqual(list(actual), expected)

    @mock.patch('my_wallet.stocks.models.find_quote_day')
    def test_prices_year_change(self, find_quote_day):
        find_quote_day.side_effect = [
            datetime(2019, 1, 1).date(), datetime(2017, 12, 31).date()
        ]
        actual = Prices.objects.year_change()
        perc_change = (self.price1.price / self.price4.price - 1) * 100
        expected = [[self.apple.ticker, perc_change], ]
        self.assertEqual(actual, expected)

    def test_financial_properties(self):
        equity_expected = self.financial.assets - self.financial.liabilities
        equity_actual = self.financial.equity
        self.assertEqual(equity_actual, equity_expected)

        net_margin_expected = self.financial.net_income / self.financial.total_revenue
        net_margin_actual = self.financial.net_margin
        self.assertEqual(net_margin_actual, net_margin_expected)

        roe_expected = self.financial.net_income / self.financial.equity
        roe_actual = self.financial.roe
        self.assertEqual(roe_actual, roe_expected)

    def test_dividend_which_quarter(self):
        actual = self.dividend.which_quarter()
        expected = '1Q 2019'
        self.assertMultiLineEqual(actual, expected)

    def test_dividend_get_rate_valid(self):
        actual = self.dividend.get_rate
        expected = (
            Decimal(self.dividend.amount/self.price1.price * 100)
            .quantize(percents, ROUND_HALF_UP))
        self.assertEqual(actual, round(expected, 4))

    def test_dividend_get_rate_invalid(self):
        new_dividend = Dividends.objects.create(
            stock=self.apple, payment=datetime(2019, 2, 1).date(),
            record=datetime(2018, 2, 4).date(), amount=2)
        actual = new_dividend.get_rate
        expected = 'No data'
        self.assertMultiLineEqual(actual, expected)
