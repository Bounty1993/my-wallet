from django.db import models
from decimal import Decimal
import datetime
from django.utils import timezone
import pytz
import requests
from my_wallet.stocks.models import Stocks
from my_wallet.profiles.models import Profile
from django.urls import reverse


class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, related_name='portfolio',
                                on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=11, decimal_places=2)
    cash = models.DecimalField(max_digits=11, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=250, blank=True)
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:

        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('portfolioportfolio:details', kwargs={'name': self.name})

    @property
    def stocks_value(self):
        total_value = 0
        for asset in self.asset:
            total_value += asset.value
        return total_value

    @property
    def total_value(self):
        return self.stocks_value + self.cash

    @property
    def total_return(self):
        return self.total_value - self.beginning_cash

    @property
    def percent_return(self):
        return (self.total_return/self.beginning_cash) - 1

    def create_transaction(self, ticker, number, price, kind):
        stocks = Stocks.objects.get(ticker=ticker)
        transaction = Transaction.objects.create(
            portfolio=self,
            stocks=stocks,
            number=number,
            price=price,
            kind=kind,
            date=timezone.now()
        )
        return transaction

    def buy_transaction(self, ticker, number):
        price = Stocks.get_current_price(ticker)
        value = price * number
        if self.cash < value:
            print("Not enough money")
        self.cash -= price * number
        self.save()  # add method to change data
        transaction = self.create_transaction(
            ticker, number, price, kind='B'
        )
        transaction.buy()

    def sell_transaction(self, ticker, number):
        try:
            asset = self.asset.get(ticker=ticker)
        except Asset.DoesNotExist:
            print('You have no asset')
        else:
            price = Stocks.get_current_price(ticker)
            self.cash -= price * number
            self.save() # add method to change data
            transaction = self.create_transaction(
                ticker, number, price, kind='S'
            )
            transaction.sell(asset)


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

    def buy_modify(self, asset):
        total_cost = asset.cost * asset.number
        asset.number += self.number
        new_cost = total_cost + (self.number * self.price)
        asset.avg_cost = new_cost/asset.number

    def buy(self):
        try:
            asset = self.portfolio.asset.get(stocks=self.stocks)
        except Asset.DoesNotExist:
            self.create_asset()
        else:
            self.buy_modify(asset)

    def sell_modify(self, asset):
        total_cost = asset.cost * asset.number
        asset.number -= self.number
        new_cost = total_cost - (self.number * self.price)
        asset.avg_cost = new_cost/asset.number

    def sell(self, asset):
        if self.number == asset.number:
            asset.is_open = False
            asset.save()  # add proper method
        else:
            self.sell_modify(asset)



