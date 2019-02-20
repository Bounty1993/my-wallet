from django.db import models
import datetime
import requests
from my_wallet.stocks.models import Stocks
from my_wallet.profiles.models import Profile


class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, related_name='portfolio',
                                on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=11, decimal_places=2)
    cash = models.DecimalField(max_digits=11, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=250, blank=True)
    is_visible = models.BoolenField()
    is_active = models.BoolenField()
    destroyed = models.DateTimeField()

    class Meta:

        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return self.name

    def get_total_wealth(self):
        # returns Profile's wealth (all Assets * number of shares
        total_wealth = 0
        for asset in self.assets:
            current_value = asset.get_current_value()
            total_wealth += current_value
        return total_wealth

    def get_summary(self):
        # return most important data to show in templates
        data = {}
        if self.assets.exists():
            for asset in self.assets:
                data.update({asset.stock.name: asset.get_current_price()})
            return data
        return data

    def has_asset(self, portfolio, ticker):
        try:
            shares = self.asset.get(stocks__ticker=ticker)
        except Asset.DoesNotExist:
            shares = None
        return shares

    def modify_assets(self, ticker, number):
        pass

    def buy_asset(self, ticker, number):
        price = Stocks.get_current_price(ticker)
        self.cash -= price * number
        stocks = Stocks.objects.get(ticker=ticker)
        Transaction.objects.create(
            portfolio=self,
            stocks=stocks,
            number=number,
            kind='B',
            date=datetime.datetime.now()
        )
        self.modify_assets(ticker, number)

    def make_transaction(self, ticker, number, kind):
        if kind == 'BUY':
            self.buy_asset(ticker, number)
        else:
            self.sell_asset(ticker, number)


class Asset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,
                                  related_name='asset')
    stocks = models.ForeignKey(Stocks, on_delete=models.PROTECT)
    num_of_shares = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_add_now=True)
    sold = models.DateTimeField(blank=True)

    class Meta:

        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        ordering = ('created_at',)

    def get_current_price(self):
        url = 'https://api.iextrading.com/1.0/stock/{}/book'.format(self.stock.ticker)
        response = requests.get(url)
        prices = response.json()
        return prices['quote']['latestPrice']

    def get_current_value(self):
        current_value = self.get_current_price() * self.num_of_shares
        return current_value


class Transaction(models.Model):
    KIND = (
        ('S', 'SELL'),
        ('B', 'BUY')
    )
    portfolio = models.ForeignKey(Portfolio, related_name='transaction',
                                  on_delete=models.CASCADE)
    stocks = models.ForeignKey(Stocks, on_delete=models.PROTECT)
    number = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    kind = models.CharField(max_length=4, choices=KIND)
    date = models.DateTimeField()
