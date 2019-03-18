#!/usr/bin/python

from my_wallet.stocks.utils import StockMaker

with open('my_wallet/stocks/fixtures.txt') as file:
    for ticker in file:
        StockMaker(ticker.strip()).add_all()

