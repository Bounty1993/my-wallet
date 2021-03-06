import datetime
import math
from decimal import ROUND_HALF_UP, Decimal

from django.core.cache import cache
from django.db import models
from django.db.models import Count, Max, Min, Q, Sum
from django.utils import timezone

from .crawler import QuotesIEX


def find_quote_day(date, days_ago=0, type='earlier'):
    """
    Function is responsible for finding the nearest quote day in the past.
    First function get the starting date (:date: - :days_ago:). Next function
    found the nearest working day :earlier: or :later:
    E.G. (if type = 'earlier')
        starting date = Sunday -> return = Friday
        starting date = Friday -> return = Saturday
    :param date: the beginning date: datetime
    :param days_ago: how many days from the beginning date: int
    :param type: can be 'earlier' or 'later': str
    :return: datetime
    """
    quote_day = date - timezone.timedelta(days=days_ago)

    if type == 'earlier':
        if quote_day.weekday() == 6:
            quote_day -= timezone.timedelta(days=2)
            return quote_day
        elif quote_day.weekday() == 0:
            quote_day -= timezone.timedelta(days=3)
            return quote_day
        quote_day -= timezone.timedelta(days=1)
        return quote_day
    elif type == 'later':
        if quote_day.weekday() == 5:
            quote_day += timezone.timedelta(days=2)
            return quote_day
        elif quote_day.weekday() == 4:
            quote_day += timezone.timedelta(days=3)
            return quote_day
        quote_day += timezone.timedelta(days=1)
        return quote_day
    else:   # pragma: no cover
        raise ValueError('Not correct type')


class StockManager(models.Manager):
    def highest_dividends(self):
        """
        classmethod responsible for collect data about dividends rate.
        Dividends model is used. Reversed sorted dict is returned
        :return: format {'ticker': ..., 'sum_dividends': data in percent}
        """
        year_ago = datetime.date.today() - datetime.timedelta(days=365)
        last_year = Sum('dividends__amount', filter=Q(dividends__payment__gte=year_ago))
        data = self.values('ticker').annotate(sum_dividends=last_year)
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


class Stocks(models.Model):
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=10)

    objects = StockManager()

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

    def dividend_amount(self):
        year_ago = datetime.date.today() - datetime.timedelta(days=365)
        four_quarters = self.dividends.filter(payment__gte=year_ago)
        data = four_quarters.aggregate(amount=Sum('amount'))
        return data['amount'] or 0

    def dividend_rate(self):
        price = cache.get(self.ticker + '_price')
        if not price:
            return 'Brak'
        price = Decimal(price)
        return (self.dividend_amount()/price) * 100

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

    def dividends_summarize(self):
        past_dividends = []
        if not self.dividends.exists():
            return []  # None will cause error in pagination
        for dividend in self.dividends.all():
            one_quarter = {
                'payment': dividend.payment,
                'record': dividend.record,
                'amount': dividend.amount,
                'quarter': dividend.which_quarter()
             }
            past_dividends.append(one_quarter)
        return past_dividends

    def get_change(self, num_days):
        today = timezone.now().date()
        past_date = today - datetime.timedelta(days=num_days)
        try:
            data = self.past.filter(date_price__gte=past_date)
            current_price = list(data)[-1].price
            past_price = list(data)[0].price
        except (AttributeError, IndexError):
            return {'currency': 'No data', 'percent': 'no data'}
        currency = current_price - past_price
        percent = ((current_price/past_price)-1) * 100

        return {'currency': currency, 'percent': percent}


class StockDetail(models.Model):
    stock = models.OneToOneField(
        Stocks, on_delete=models.CASCADE, related_name='detail')
    sector = models.CharField(max_length=200)
    industry = models.CharField(max_length=200)
    website = models.URLField(null=True, blank=True)
    description = models.CharField(max_length=5000)

    class Meta:
        verbose_name = 'stock details'
        ordering = ('sector', )


class Dividends(models.Model):
    stock = models.ForeignKey(
        Stocks, on_delete=models.CASCADE, related_name='dividends')
    payment = models.DateField(null=True, blank=True)
    record = models.DateField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=11, decimal_places=2, null=True, blank=True)

    @property
    def get_rate(self):
        percents = Decimal('0.0001')
        price = Prices.objects.filter(stock=self.stock, date_price=self.record)
        if price:
            price = price[0].price
            return Decimal(self.amount/price * 100).quantize(percents, ROUND_HALF_UP)
        return 'No data'

    def which_quarter(self):
        present_quarter = math.ceil(self.record.month / 3)
        return f'{present_quarter}Q {self.record.year}'

    def __str__(self):
        return f'{self.stock} - {self.payment}'

    class Meta:
        ordering = ('-payment', )


class Financial(models.Model):
    stock = models.ForeignKey(
        Stocks, on_delete=models.CASCADE, related_name='financial')
    assets = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    liabilities = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    total_revenue = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    gross_profit = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True)
    operating_income = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True)
    net_income = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True)

    @property
    def equity(self):
        return self.assets - self.liabilities

    @property
    def net_margin(self):
        return self.net_income / self.total_revenue

    @property
    def roe(self):
        return self.net_income/self.equity

    class Meta:
        verbose_name = 'financial results'
        ordering = ('-total_revenue', )


class PriceManager(models.Manager):
    def year_change(self):
        today = datetime.datetime.now().date()
        present_date = find_quote_day(today, days_ago=50)
        past_date = find_quote_day(today, days_ago=365)
        data = (
            self.values_list('stock__ticker', 'date_price', 'price')
                .filter(date_price__in=[present_date, past_date])
                .order_by('stock__ticker')
        )
        results = {}
        for (ticker, _, price) in data:
            if not ticker in results:
                results[ticker] = [price, ]
            else:
                results[ticker].append(price)
        final = []
        for (key, values) in results.items():
            if len(values) == 2:
                perc_return = ((values[0] / values[1]) - 1) * 100
                final.append([key, perc_return])
        return sorted(final, key=lambda x: x[1])


class Prices(models.Model):
    stock = models.ForeignKey(
        Stocks, on_delete=models.CASCADE,
        related_name='past'
    )
    price = models.DecimalField(
        max_digits=11, decimal_places=2, null=True, blank=True)
    open = models.DecimalField(
        max_digits=11, decimal_places=2, null=True, blank=True)
    volume = models.PositiveIntegerField(null=True, blank=True)
    change = models.FloatField(null=True, blank=True)
    percent_change = models.FloatField(null=True, blank=True)
    date_price = models.DateField()

    objects = PriceManager()

    class Meta:
        get_latest_by = 'date_price'
        ordering = ('-date_price',)
