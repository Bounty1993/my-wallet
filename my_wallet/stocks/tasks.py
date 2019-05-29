from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task

import requests
from .models import Prices, Stocks


@shared_task
def update_stock_price():
    print('Running task update stocks')
    tickets = Stocks.objects.values_list('ticker', flat=True)
    for ticket in tickets:
        url = f'https://api.iextrading.com/1.0/stock/{ticket}/previous'
        data = requests.get(url).json()
        print(data)
        Prices.objects.create(
            stock=Stocks.objects.get(ticker__iexact=data.get('symbol')),
            price=float(data.get('close')),
            date_price=data.get('date') if data.get('date') else None,
            open=data.get('open') if data.get('open') else None,
            volume=data.get('volume') if data.get('volume') else None,
            change=data.get('change') if data.get('change') else None,
            percent_change=data.get('changePercent') if data.get('changePercent') else None,
        )
        print(f'Updated prices for {ticket}')
        logging.info(f'Updated prices for {ticket} logging')