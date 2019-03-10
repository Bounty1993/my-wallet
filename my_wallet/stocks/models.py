from django.db import models
from django.db.models import Max, Min
from django.utils import timezone
import requests
import datetime
from .crawler import (
    QuotesIEX,
    CompanyIEX,
    PastIEX,
    DividendsIEX,
    FinancialIEX,
)
from decimal import Decimal, ROUND_HALF_UP


def find_quote_day(date, num_days=0, type='earlier'):
    quote_day = date - timezone.timedelta(days=num_days)

    if type == 'earlier':
        if quote_day.weekday() == 6:
            quote_day -= timezone.timedelta(days=2)
            return quote_day
        return quote_day

    elif type == 'later':
        if quote_day.weekday() == 6:
            quote_day -= datetime.timedelta(days=2)
            return quote_day
        quote_day -= datetime.timedelta(days=1)
        return quote_day


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


class StockDetail(models.Model):
    stock = models.OneToOneField(Stocks, on_delete=models.CASCADE, related_name='detail')
    sector = models.CharField(max_length=50)
    industry = models.CharField(max_length=50)
    website = models.URLField(null=True, blank=True)
    description = models.CharField(max_length=500)

    class Meta:
        verbose_name = 'stock details'
        ordering = ('sector', )


class Dividends(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='dividends')
    payment = models.DateField(null=True, blank=True)
    record = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)

    @property
    def get_rate(self):
        # to do for 4 quarters
        percents = Decimal('0.0001')
        price = Prices.objects.get(stock=self.stock, date_price=self.record).price
        return Decimal(self.amount/price * 100).quantize(percents, ROUND_HALF_UP)

    class Meta:
        ordering = ('-payment', )


class Financial(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE, related_name='financial')
    assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    liabilities = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    gross_profit = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    operating_income = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    net_income = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

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
        ordering = ('-total_revenue', )


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
    open = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    volume = models.PositiveIntegerField(null=True, blank=True)
    change = models.FloatField(null=True, blank=True)
    percent_change = models.FloatField(null=True, blank=True)
    date_price = models.DateField(null=True, blank=True)


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
