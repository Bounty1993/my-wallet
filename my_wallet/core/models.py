from django.db import models

import requests

from my_wallet.profiles.models import Profile


class Stocks(models.Model):
    name = models.CharField(max_length=50)
    ticker = models.CharField(max_length=10, unique_for_date='date_price')
    price = models.DecimalField(max_digits=11, decimal_places=2)
    date_price = models.DateField()

    def get_past_data(self):
        url = 'https://api.iextrading.com/1.0/stock/{}/chart/5y'.format(self.ticker)
        response = requests.get(url)
        prices = response.json()
        for data in prices:
            Stocks.objects.create(name=self.name,
                                  ticker=self.ticker,
                                  price=float(data.get('close')),
                                  date_price=data.get('date')
            )


class Asset(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    bought_for = models.DecimalField(max_digits=11, decimal_places=2)
    num_of_shares = models.PositiveIntegerField()
    created_at = models.DateField()

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

    def get_total_wealth(self):
        total_wealth = 0
        for asset in self.assets:
            current_value = asset.get_current_value()
            total_wealth += current_value
        return total_wealth

    def get_summary(self):
        data = {}
        if self.assets.exists():
            for asset in self.assets:
                data.update({asset.stock.name: asset.get_current_price()})
            return data
        return data


