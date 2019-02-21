from django.db import models
from django.db.models import Max, Min
import requests
import datetime
from .crawler import quotes_IEX
from .utils import find_quote_day


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

    @staticmethod
    def get_current_price(ticker):
        return quotes_IEX(ticker)['latestPrice']

    def get_past_data(self):
        # returns past prices of a Stocks' instance (last 5 years)
        url = 'https://api.iextrading.com/1.0/stock/{}/chart/5y'.format(self.ticker)
        response = requests.get(url)
        prices = response.json()
        for data in prices:
            Prices.objects.create(stock=self,
                                  price=float(data.get('close')),
                                  date_price=data.get('date'))

    def year_change(self):

        today = datetime.datetime.now().date()
        current_date = find_quote_day(date=today)

        while True:
            try:
                current_price = self.prices.get(date_price=current_date)
                current_price = current_price.price
            except Prices.DoesNotExist:
                current_date -= datetime.timedelta(days=1)
            else:
                break

        past_date = find_quote_day(date=today, num_days=365)
        while True:
            try:
                past_price = self.prices.get(date_price=past_date)
                past_price = past_price.price
            except Prices.DoesNotExist:
                past_date += datetime.timedelta(days=1)
            else:
                break

        currency = current_price - past_price
        perc_change = (current_price/past_price)-1
        percent = '{:.2%}'.format(perc_change)

        return {'currency': currency, 'percent': percent}

    @classmethod
    def get_stocks_with_data(cls, ticker):

        quotes = quotes_IEX(ticker)

        data = {'name': quotes['companyName'],
                'ticker': quotes['symbol']
                }
        stock = cls.objects.create(name=data['name'],
                                   ticker=data['ticker'])
        stock.get_past_data()
        return stock

    @staticmethod
    def get_updated():
        pass

    def get_min_and_max(self, start, end):
        """
        give start and end as a datetime.
        function returns min and max price.
        """

        prices_between = self.prices.filter(date_price__gte=start)
        prices_between = prices_between.filter(date_price__lte=end)
        data = prices_between.aggregate(Max('price'), Min('price'))

        return data


class Prices(models.Model):

    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE,
                              related_name='prices')
    price = models.DecimalField(max_digits=11, decimal_places=2)
    date_price = models.DateField()

    class Meta:
        get_latest_by = 'date_price'
        ordering = ('-date_price',)
