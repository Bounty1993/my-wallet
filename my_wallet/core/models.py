import datetime

from my_wallet.stocks.models import Stocks
from django.db import models

import requests

from my_wallet.profiles.models import Profile


class Asset(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    bought_for = models.DecimalField(max_digits=11, decimal_places=2)
    num_of_shares = models.PositiveIntegerField()
    created_at = models.DateField()

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


class Portfolio(models.Model):
    profile = models.OneToOneField(Profile, related_name='portfolio',
                                   on_delete=models.CASCADE)
    assets = models.ManyToManyField(Asset)

    class Meta:

        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return self.profile

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


