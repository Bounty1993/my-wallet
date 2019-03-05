# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from my_wallet.stocks.crawler import quotes_IEX
from my_wallet.stocks.models import CurrentPrice, Stocks
from django.utils import timezone
from decimal import Decimal


@shared_task
def price_update():
    for stock in Stocks.objects.all():
        price = Decimal(quotes_IEX(stock.ticker)['latestPrice'])
        CurrentPrice.objects.create(
            stock=stock,
            price=price,
            date_price=timezone.now()
        )
    print('I have finished')


@shared_task
def past_price_update():
    pass



