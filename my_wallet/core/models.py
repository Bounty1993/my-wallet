from django.db import models
from decimal import Decimal
import datetime
from django.utils import timezone
import pytz
import requests
from my_wallet.stocks.models import Stocks
from my_wallet.profiles.models import Profile


class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, related_name='portfolio',
                                on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=11, decimal_places=2)
    current_cash = models.DecimalField(max_digits=11, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=250, blank=True)
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

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

    def create_transaction(self, ticker, number, price):
        stocks = Stocks.objects.get(ticker=ticker)
        transaction = Transaction.objects.create(
            portfolio=self,
            stocks=stocks,
            number=number,
            price=price,
            kind='B',
            date=timezone.now()
        )
        return transaction

    def buy_asset(self, ticker, number):
        price = Stocks.get_current_price(ticker)
        self.current_cash -= price * number
        self.save()
        transaction = self.create_transaction(
            ticker, number, price
        )
        transaction.buy_update()

    def sell_asset(self, ticker, number):
        pass

    def make_transaction(self, ticker, number, kind):
        if kind == 'B':
            self.buy_asset(ticker, number)
        else:
            self.sell_asset(ticker, number)


class Asset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,
                                  related_name='asset')
    stocks = models.ForeignKey(Stocks, on_delete=models.PROTECT)
    avg_cost = models.DecimalField(max_digits=7, decimal_places=2)
    sum_number = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
    is_open = models.BooleanField(default=True, blank=True)

    class Meta:

        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'


class Transaction(models.Model):
    KIND = (
        ('S', 'SELL'),
        ('B', 'BUY')
    )
    portfolio = models.ForeignKey(Portfolio, related_name='transaction',
                                  on_delete=models.CASCADE)
    stocks = models.ForeignKey(Stocks, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    number = models.PositiveIntegerField()
    kind = models.CharField(max_length=4, choices=KIND)
    date = models.DateTimeField()

    def create_asset(self):
        Asset.objects.create(
            portfolio=self.portfolio,
            stocks=self.stocks,
            avg_cost=self.price,
            sum_number=self.number,
        )

    def buy_modify(self, current_asset):
        pass

    def buy_update(self):
        try:
            current_asset = self.portfolio.asset.get(stocks=self.stocks)
        except Asset.DoesNotExist:
            self.create_asset()
        else:
            self.buy_modify(current_asset)



