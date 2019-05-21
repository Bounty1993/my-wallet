from datetime import datetime
from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils import timezone

from my_wallet.profiles.models import Profile
from my_wallet.stocks.models import Stocks


class Portfolio(models.Model):
    name = models.CharField('nazwa', max_length=50)
    profile = models.ForeignKey(Profile, related_name='portfolio',
                                on_delete=models.CASCADE, verbose_name='profil')
    beginning_cash = models.DecimalField('początkowa gotówka', max_digits=11, decimal_places=2)
    cash = models.DecimalField('gotówka', max_digits=11, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField('opis', max_length=250, blank=True)
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:

        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('portfolio:details', kwargs={'name': self.name})

    @property
    def stocks_value(self):
        total_value = 0
        for asset in self.asset.all():
            total_value += asset.stocks.current_price * asset.sum_number
        return total_value

    @property
    def total_value(self):
        return Decimal(self.stocks_value) + self.cash

    @property
    def total_return(self):
        return self.total_value - self.beginning_cash

    @property
    def percent_return(self):
        return self.total_return/self.beginning_cash * 100

    def buy(self, number, stock, price):
        total_value = number * price
        asset = self.asset.filter(stocks=stock)
        if asset.count() == 1:
            asset = asset.first()
            self.cash -= total_value
            new_cost = asset.total_cost + total_value
            asset.avg_cost = new_cost / (asset.sum_number + number)
            asset.sum_number += number
            asset.save()
            self.save()
        else:
            self.cash -= total_value
            Asset.objects.create(
                portfolio=self,
                stocks=stock,
                avg_cost=total_value,
                sum_number=number
            )
            self.save()

    def sell(self, number, stock, price):
        total_value = number * price
        asset = self.assets.get(stocks=stock)
        self.cash += total_value
        new_cost = asset.total_cost - total_value
        asset.avg_cost = new_cost / (asset.sum_number - number)
        asset.sum_number -= number
        asset.save()
        self.save()
        if asset.sum_number == 0:
            asset.delete()

    def is_new(self):
        if self.created_at == datetime.now().date:
            return True
        return False

    def has_transactions(self):
        older = self.transaction.filter(date__lte=datetime.now().date)
        if older.exists():
            return True

    def make_past_portfolio(self):
        PastPortfolio.objects.create(
            parent=self,
            beginning_cash=self.beginning_cash,
            cash=self.cash,
            stock_value=self.stocks_value
        )


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

    @property
    def total_cost(self):
        return self.avg_cost * self.sum_number


class Transaction(models.Model):
    KIND = (
        ('S', 'SELL'),
        ('B', 'BUY')
    )
    portfolio = models.ForeignKey(Portfolio, related_name='transaction',
                                  on_delete=models.CASCADE)
    stocks = models.ForeignKey(Stocks, on_delete=models.PROTECT)
    price = models.DecimalField('cena', max_digits=7, decimal_places=2)
    number = models.PositiveIntegerField()
    kind = models.CharField('rodzaj', max_length=4, choices=KIND)
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:

        ordering = ('-date',)

    @property
    def cost(self):
        return self.price * self.number

    def get_price(self):
        self.price = Decimal(Stocks.get_current_price(self.stocks.ticker))

class PastPortfolio(models.Model):
    parent = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=11, decimal_places=2)
    cash = models.DecimalField(max_digits=11, decimal_places=2)
    stock_value = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField('date', auto_now_add=True)

