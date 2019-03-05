from django.db import models
from django.db.models import Max, Min
from django.utils import timezone
import requests
import datetime
from .crawler import (
    QuotesIEX,
    CompanyIEX,
    PastIEX,
    DividendsIEX
    FinancialIEX
)
from .utils import find_quote_day
from decimal import Decimal, ROUND_HALF_UP


class Stocks(models.Model):
    """
    Model is responsible for keeping data about every stock.
    Other models can use data from Stocks to get to know everything about
    past prices
    """
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=10)

    class Meta:

        verbose_name = 'Stocks'
        verbose_name_plural = 'Stocks'
        ordering = ('ticker',)

    def __str__(self):
        return self.name

    @property
    def price(self):
        cents = Decimal('0.01')
        price = QuotesIEX(self.ticker).get_data().get('latestPrice', '')
        return Decimal(price).quantize(cents, ROUND_HALF_UP)

    @property
    def year_change(self):
        return self.get_change(num_days=365)['currency']

    @property
    def perc_year_change(self):
        return self.get_change(num_days=365)['percent']

    @property
    def daily_change(self):
        return self.get_change(num_days=1)['currency']

    @property
    def perc_daily_change(self):
        return self.get_change(num_days=1)['percent']

    @property
    def min_daily(self):
        start = timezone.now().date() - timezone.timedelta(days=1)
        return self.get_min_and_max(start=start, end=timezone.now())['price__min']

    @property
    def max_daily(self):
        start = timezone.now().date() - timezone.timedelta(days=1)
        return self.get_min_and_max(start=start, end=timezone.now())['price__max']

    @staticmethod
    def get_current_price(ticker):
        return QuotesIEX(ticker).get_data().get('latestPrice', '')

    def find_past_price(self, num_days):
        today = timezone.now().date()
        past_date = find_quote_day(date=today, num_days=num_days)
        while True:
            try:
                past_price = self.past.get(date_price=past_date).price
            except Prices.DoesNotExist:
                past_date -= datetime.timedelta(days=1)
            else:
                break
        return past_price

    def get_change(self, num_days):
        current_price = self.current.latest('date_price').price
        past_price = self.find_past_price(num_days=num_days)
        currency = current_price - past_price
        perc_change = (current_price/past_price)-1
        percent = '{:.2%}'.format(perc_change)

        return {'currency': currency, 'percent': percent}

    def get_min_and_max(self, start, end):
        """
        give start and end as a datetime.
        function returns min and max price.
        """

        prices_between = self.current.filter(date_price__gte=start)
        prices_between = prices_between.filter(date_price__lte=end)
        data = prices_between.aggregate(Max('price'), Min('price'))

        return data

    def add_detail(self):
        # method create or update StockDetail
        data = CompanyIEX(self.ticker).get_data()

        StockDetail.objects.create(
            stock=self,
            sector=data.get('sector', ''),
            industry=data.get('industry', ''),
            website=data.get('website', ''),
            description=data.get('description', '')
        )

    def get_past_data(self):
        # past prices of a Stocks' instance (last 5 years)
        prices = PastIEX(self.ticker).get_data()
        for data in prices:
            Prices.objects.create(
                stock=self,
                price=float(data.get('close')),
                date_price=data.get('date'),
            )

    @classmethod
    def get_stocks_with_data(cls, ticker):
        # use when you create new stock class
        quotes = QuotesIEX(ticker).get_data()
        data = {
            'name': quotes['companyName'],
            'ticker': quotes['symbol']
        }
        stock = cls.objects.create(
            name=data['name'],
            ticker=data['ticker']
        )
        stock.add_detail()
        stock.get_past_data()
        return stock


class StockDetail(models.Model):
    stock = models.OneToOneField(Stocks, on_delete=models.CASCADE, related_name='detail')
    sector = models.CharField(max_length=50)
    industry = models.CharField(max_length=50)
    website = models.URLField()
    description = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'stock details'
        ordering = 'sector'


class Dividends(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='dividends')
    payment = models.DateField()
    record = models.DateField()
    amount = models.DecimalField(max_digits=11, decimal_places=2)

    @property
    def get_rate(self):
        price = Prices.objects.get(stock=self.stock, date_price=self.record).price
        return self.amount/self.price


class Financial(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='financial')
    assets = models.DecimalField(max_digits=14, decimal_places=2)
    liabilities = models.DecimalField(max_digits=14, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2)
    gross_profit = models.DecimalField(max_digits=14, decimal_places=2)
    operating_income = models.DecimalField(max_digits=14, decimal_places=2)
    net_income = models.DecimalField(max_digits=14, decimal_places=2)

    @property
    def equity(self):
        return self.assets - self.liabilities

    @property
    def operating_margin(self):
        return self.operating_income/self.total_revenue

    @property
    def net_margin(self):
        return self.net_income / self.total_revenue

    @property
    def roa(self):
        return self.net_income/self.assets

    @property
    def roe(self):
        return self.net_income/self.equity

    class Meta:
        verbose_name = 'financial results'
        ordering = '-total_revenue'


class BasePrices(models.Model):

    stock = models.ForeignKey(
        Stocks, on_delete=models.CASCADE,
        related_name='past'
    )
    price = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        abstract = True
        get_latest_by = 'date_price'
        ordering = ('-date_price',)


class Prices(BasePrices):
    date_price = models.DateField()


class CurrentPrice(BasePrices):
    stock = models.ForeignKey(
        Stocks, on_delete=models.CASCADE,
        related_name='current'
    )
    date_price = models.DateTimeField()

    def _daily_min_and_max(self):
        today = timezone.now().date()
        start = timezone.datetime(today.year, today.month, today.day)
        end = timezone.now()
        return self.get_min_and_max(start, end)
