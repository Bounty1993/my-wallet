import datetime
from django.utils import timezone
from .models import (
    Stocks,
    StockDetail,
    Dividends,
    Prices,
)
from .crawler import (
    QuotesIEX,
    CompanyIEX,
    PastIEX,
    DividendsIEX
    FinancialIEX
)


def find_quote_day(date, num_days=0, type='earlier'):
    quote_day = date - timezone.timedelta(days=num_days)

    if type == 'earlier':
        if quote_day.weekday() == 6:
            quote_day -= timezone.timedelta(days=2)
            return quote_day
        return quote_day

    elif type == 'later':
        if quote_day.weekday() == 6:
            quote_day -= datetime.timedelta(days=2)
            return quote_day
        quote_day -= datetime.timedelta(days=1)
        return quote_day


class StockMaker:
    def add_detail(self):
        # method create or update StockDetail
        data = CompanyIEX(self.ticker).get_data()

        StockDetail.objects.create(
            stock=self,
            sector=data.get('sector', ''),
            industry=data.get('industry', ''),
            website=data.get('website', ''),
            description=data.get('description', '')
        )

    def get_past_data(self):
        # past prices of a Stocks' instance (last 5 years)
        prices = PastIEX(self.ticker).get_data()
        for data in prices:
            Prices.objects.create(
                stock=self,
                price=float(data.get('close')),
                date_price=data.get('date'),
            )

    def get_stocks_with_data(self):
        # use when you create new stock class
        quotes = QuotesIEX(self.ticker).get_data()
        data = {
            'name': quotes['companyName'],
            'ticker': quotes['symbol']
        }
        stock = Stocks.objects.create(
            name=data['name'],
            ticker=data['ticker']
        )