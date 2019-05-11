import datetime
from django.utils import timezone
from .crawler import (
    QuotesIEX,
    CompanyIEX,
    PastIEX,
    DividendsIEX,
    FinancialIEX,
)
from .models import (
    Stocks,
    StockDetail,
    Dividends,
    Financial,
    Prices,
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

    def __init__(self, ticker):
        self.ticker = ticker

    def add_stocks(self):
        # use when you create new stock class
        quotes = QuotesIEX(self.ticker).get_data()
        data = {
            'name': quotes['companyName'],
            'ticker': quotes['symbol']
        }
        Stocks.objects.create(
            name=data['name'],
            ticker=data['ticker']
        )

    def add_detail(self):
        # method create or update StockDetail
        data = CompanyIEX(self.ticker).get_data()

        StockDetail.objects.create(
            stock=Stocks.objects.get(ticker=self.ticker),
            sector=data.get('sector'),
            industry=data.get('industry'),
            website=data.get('website'),
            description=data.get('description')
        )

    def add_dividends(self):
        dividends = DividendsIEX(self.ticker).get_data()
        for data in dividends:
            Dividends.objects.create(
                stock=Stocks.objects.get(ticker=self.ticker),
                payment=data.get('paymentDate') if data.get('paymentDate') else None,
                record=data.get('recordDate') if data.get('recordDate') else None,
                amount=data.get('amount') if data.get('amount') else None
            )

    def add_financial(self):
        finances = FinancialIEX(self.ticker).get_data()
        for finance in finances:
            Financial.objects.create(
                stock=Stocks.objects.get(ticker=self.ticker),
                assets=finance.get('totalAssets') if finance.get('totalAssets') else None,
                liabilities=finance.get('totalLiabilities') if finance.get('totalLiabilities') else None,
                total_revenue=finance.get('totalRevenue') if finance.get('totalRevenue') else None,
                gross_profit=finance.get('grossProfit') if finance.get('grossProfit') else None,
                operating_income=finance.get('operatingIncome') if finance.get('operatingIncome') else None,
                net_income=finance.get('netIncome') if finance.get('netIncome') else None,
            )

    def add_past_data(self):
        # past prices of a Stocks' instance (last 5 years)
        prices = PastIEX(self.ticker).get_data()
        for data in prices:
            Prices.objects.create(
                stock=Stocks.objects.get(ticker=self.ticker),
                price=float(data.get('close')),
                date_price=data.get('date') if data.get('date') else None,
                open=data.get('open') if data.get('open') else None,
                volume=data.get('volume') if data.get('volume') else None,
                change=data.get('change') if data.get('change') else None,
                percent_change=data.get('changePercent') if data.get('changePercent') else None,
            )

    def add_all(self):
        self.add_stocks()
        self.add_detail()
        self.add_dividends()
        self.add_financial()
        self.add_past_data()
        print(f'date for {self.ticker} collected')
