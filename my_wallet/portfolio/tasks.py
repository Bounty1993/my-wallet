# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.cache import cache
from my_wallet.stocks.models import Stocks
from my_wallet.stocks.crawler import QuotesIEX


@shared_task
def price_update():
    for stock in Stocks.objects.all():
        data = QuotesIEX(stock.ticker).get_data()
        cache.set(stock.ticker + '_price', data.get('latestPrice', 'no data'))
        cache.set(stock.ticker + '_day_change', data.get('change', 'no data'))
        cache.set(stock.ticker + '_percent_change', data.get('changePercent', 'no data') * 100)
        print(f'{stock.ticker} updated successfully')

    print('I have finished')




