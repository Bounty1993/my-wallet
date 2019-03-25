from django.db import models
from django.db.models import Max, Min, Sum, Count, Q
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
from django.core.cache import cache


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
        Model keeps data about every stock.
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
    def current_price(self):
        return cache.get(self.ticker + '_price')

    @property
    def day_change(self):
        return cache.get(self.ticker + '_day_change')

    @property
    def percent_change(self):
        return cache.get(self.ticker + '_percent_change')

    @property
    def day_low(self):
        return cache.get(self.ticker + '_day_low')

    @property
    def day_high(self):
        return cache.get(self.ticker + '_day_high')

    @property
    def year_change(self):
        return self.get_change(num_days=365)['currency']

    @property
    def perc_year_change(self):
        return self.get_change(num_days=365)['percent']

    @property
    def dividend_amount(self):
        year_ago = datetime.date.today() - datetime.timedelta(days=365 * 2)
        four_quarters = self.dividends.filter(payment__gte=year_ago)
        data = four_quarters.aggregate(amount=Sum('amount'))
        return data['amount']

    @property
    def dividend_rate(self):
        price = cache.get(self.ticker + '_price')
        if not price:
            return 'No data'
        price = Decimal(price)
        return self.dividend_amount/price

    @staticmethod
    def get_current_price(ticker):
        return QuotesIEX(ticker).get_data().get('latestPrice', '')

    def find_past_price(self, num_days):
        today = timezone.now().date()
        past_date = today - datetime.timedelta(days=num_days)

        while True:
            try:
                past_price = self.past.get(date_price=past_date).price
            except Prices.DoesNotExist:
                past_date -= datetime.timedelta(days=1)
            else:
                break
        return past_price

    def get_change(self, num_days):
        today = timezone.now().date()
        past_date = today - datetime.timedelta(days=num_days)
        try:
            data = self.past.filter(date_price__gte=past_date)
            current_price = list(data)[0].price
            past_price = list(data)[-1].price
        except (AttributeError, IndexError):
            return {'currency': 'No data', 'percent': 'no data'}
        currency = current_price - past_price
        percent = ((current_price/past_price)-1) * 100

        return {'currency': currency, 'percent': percent}

    @classmethod
    def highest_dividends(cls):
        """
        classmethod responsible for collect data about dividends rate.
        Dividends model is used. Reversed sorted dict is returned
        :return: format {'ticker': ..., 'sum_dividends': data in percent}
        """
        year_ago = datetime.date.today() - datetime.timedelta(days=365 * 2)
        last_year = Sum('dividends__amount', filter=Q(dividends__payment__gte=year_ago))
        data = cls.objects.values('ticker').annotate(sum_dividends=last_year)
        for line in data:
            dividend = line['sum_dividends']
            dividend = dividend if dividend else 0
            price = cache.get(line['ticker'] + '_price')
            if price:
                price = Decimal(price)
            percents = Decimal('0.0001')
            dividend = dividend/price if price else None
            if dividend:
                line['sum_dividends'] = Decimal(dividend * 100).quantize(percents, ROUND_HALF_UP)
            else:
                line['sum_dividends'] = 0
        data = sorted(data, key=lambda line: line['sum_dividends'], reverse=True)
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
        price = Prices.objects.filter(stock=self.stock, date_price=self.record)
        if price:
            price = price[0].price
            return Decimal(self.amount/price * 100).quantize(percents, ROUND_HALF_UP)
        return 'No data'

    @classmethod
    def year_rate(self):
        percents = Decimal('0.0001')
        year_ago = datetime.date.today() - datetime.timedelta(days=365)
        price = self.stock.current_price
        last_dividends = Dividends.objects.filter(stock=self.stock, payment__gte=year_ago)
        sum_dividends = last_dividends.aggragate(year_dividend=Sum('amount'))
        return sum_dividends

    def __str__(self):
        return f'{self.stock} - {self.payment}'

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


class Prices(models.Model):
    stock = models.ForeignKey(
        Stocks, on_delete=models.CASCADE,
        related_name='past'
    )
    price = models.DecimalField(max_digits=11, decimal_places=2)
    open = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    volume = models.PositiveIntegerField(null=True, blank=True)
    change = models.FloatField(null=True, blank=True)
    percent_change = models.FloatField(null=True, blank=True)
    date_price = models.DateField(null=True, blank=True)

    class Meta:
        get_latest_by = 'date_price'
        ordering = ('-date_price',)

    @classmethod
    def year_change(cls, ticker, num_days=365):
        today = timezone.now().date()
        past_day = today - datetime.timedelta(days=num_days)
        instance = cls.objects.filter(stock__ticker=ticker)
        data = instance.filter(data_price__gte=past_day, data_price__lte=today)
        current = data.first().price
        past = data.last().price
        return ((current.price / past.price)-1) * 100
