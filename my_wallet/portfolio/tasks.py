# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from my_wallet.stocks.crawler import quotes_IEX
from my_wallet.stocks.models import CurrentPrice, Stocks
from django.utils import timezone
from decimal import Decimal
from my_wallet.stocks.crawler import QuotesIEX


@shared_task
def price_update():
    for stock in Stocks.objects.all():
        price = Decimal(QuotesIEX(stock.ticker).get_data().get('latestPrice'))
        CurrentPrice.objects.create(
            stock=stock,
            price=price,
            date_price=timezone.now()
        )
    print('I have finished')


@shared_task
def past_price_update():
    pass



