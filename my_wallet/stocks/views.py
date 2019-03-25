from django.views.generic import (
    ListView, DetailView,
    CreateView, TemplateView
)
from django.core.cache import cache
from .models import Stocks, Prices, Dividends, Financial
import datetime
from django.utils import timezone
from .forms import NewStockForm
from .crawler import (
    GoogleCrawler,
    YahooCrawler,
    BloombergCrawler,
)
from .utils import find_quote_day
from django_tables2 import RequestConfig
from .tables import (
    DividendTable,
    PricesTable,
    BestWorstTable,
    BestDividendsTable
)
from django.http import HttpResponse
import csv



def download_csv(request):
    model = Prices
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model}.csv"'

    writer = csv.writer(response)
    # writer.writerow()
    items = model.objects.filter(stock__ticker='AAPL').values_list()

    for item in items:
        writer.writerow(item)

    return response


class CurrentPriceMixin:
    def current_data(self, object, context):
        attributes = ['_price', '_day_change', '_percent_change']
        for attribute in attributes:
            ticker = object.ticker
            result = cache.get(ticker + attribute, 'no data')
            context['stocks' + attribute] = result
    def current_data_one(self, object):
        data = {}
        attributes = ['_price', '_day_change', '_percent_change']
        for attribute in attributes:
            ticker = object.ticker
            result = cache.get(ticker + attribute, 'no data')
            data['stocks' + attribute] = result
        return data


class BestWorstMixin:

    def change_table(self):
        sorted_stocks = sorted(Stocks.objects.all(), key=lambda stock: stock.perc_year_change)
        rising_table = BestWorstTable(sorted_stocks[-5:])
        RequestConfig(self.request, paginate={'per_page': 5}).configure(rising_table)
        falling_table = BestWorstTable(sorted_stocks[:5])
        RequestConfig(self.request, paginate={'per_page': 5}).configure(falling_table)
        return {'rising_table': rising_table, 'falling_table': falling_table}


class BestDividendsMixin:

    def get_data(self, n):
        data = Stocks.highest_dividends()
        best = data[:n]
        return best

    def dividend_table(self):
        data = self.get_data(5)
        table = BestDividendsTable(data)
        RequestConfig(self.request).configure(table)
        return table


class StocksListView(BestWorstMixin, ListView):
    model = Stocks
    template_name = 'stocks/list.html'
    context_object_name = 'stocks'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = timezone.now().date()
        data_table = self.change_table()
        context['rising_table'] = data_table['rising_table']
        context['falling_table'] = data_table['falling_table']
        context['today'] = find_quote_day(date, 0, type='earlier')
        return context


class ChartMixin:

    def get_earnings_data(self, earnings_names):
        finance_data = []
        for name in earnings_names:
            data = [float(field) for field in self.instance.values_list(name, flat=True) if field]
            finance_data.append({'name': name, 'data': data})
        return finance_data

    def get_balance_data(self, balance_names):
        balance_data = self.get_earnings_data(balance_names)
        for field in balance_data:
            if field['name'] == 'assets':
                a_data = field['data']
            else:
                l_data = field['data']
        equity = [assets-liabilities for (assets, liabilities) in zip(a_data, l_data)]
        balance_data.append({'name': 'equity', 'data': equity})
        return balance_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finance_data'] = self.get_earnings_data(self.earnings_names)
        context['balance_data'] = self.get_balance_data(self.balance_names)
        return context


class PriceChartMixin:

    def get_instance(self):
        pass

    def get_num_seconds(self, date):
        epoch = datetime.date(1970, 1, 1)
        num_seconds = (date - epoch).total_seconds()*1000
        return int(num_seconds)

    def get_price_data(self, name):
        instance = self.get_instance()
        prices = [(self.get_num_seconds(field.date_price), float(field.price)) for field in instance]
        # need to debug
        price_data = {'name': name, 'prices': prices}
        return price_data


class StockDetailView(ChartMixin, CurrentPriceMixin, DetailView):
    template_name = 'stocks/detail.html'
    model = Stocks
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    earnings_names = [
        'total_revenue', 'gross_profit',
        'operating_income', 'net_income',
    ]
    balance_names = ['assets', 'liabilities']

    def get_context_data(self, **kwargs):
        self.instance = Financial.objects.filter(stock=self.object)
        context = super().get_context_data(**kwargs)
        table = DividendTable(Dividends.objects.filter(stock=self.object))
        RequestConfig(self.request, paginate={'per_page': 8}).configure(table)
        context['table'] = table
        context['last_dividend'] = Dividends.objects.filter(stock=self.object).latest('payment')
        self.current_data(self.object, context)
        return context


class StockCreateView(CreateView):
    template_name = 'stocks/new.html'
    form_class = NewStockForm

    def post(self, *args, **kwargs):
        pass


class ArticlesView(BestDividendsMixin, TemplateView):
    template_name = 'stocks/articles.html'

    def market_ticker(self):
        ticker = self.kwargs.get('ticker')
        market = 'NASDAQ'
        return market, ticker

    def process_context(self, market, ticker, context):
        google_art = GoogleCrawler(market, ticker)
        context['google_news'] = google_art.get_data()
        yahoo_art = YahooCrawler(ticker)
        context['yahoo_news'] = yahoo_art.get_data()
        # bloomberg_art = BloombergCrawler(ticker)
        # context['bloomberg_news'] = bloomberg_art.get_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        market, ticker = self.market_ticker()
        context['dividend_table'] = self.dividend_table()
        self.process_context(market, ticker, context)
        return context


class HistoryView(PriceChartMixin, CurrentPriceMixin, DetailView):
    template_name = 'stocks/history.html'
    slug_field = 'ticker'
    model = Prices

    def get_instance(self):
        return Prices.objects.filter(stock__ticker=self.kwargs['ticker']).order_by('date_price')

    def get_object(self):
        ticker = self.kwargs.get('ticker', '')
        obj = Prices.objects.filter(stock__ticker=ticker)
        return obj

    def change_table(self):
        sorted_stocks = sorted(Stocks.objects.all(), key=lambda stock: stock.perc_year_change)
        rising_table = BestWorstTable(sorted_stocks[-5:])
        RequestConfig(self.request, paginate={'per_page': 5}).configure(rising_table)
        falling_table = BestWorstTable(sorted_stocks[:5])
        RequestConfig(self.request, paginate={'per_page': 5}).configure(falling_table)
        return {'rising_table': rising_table, 'falling_table': falling_table}

    def price_table(self):
        price_table = PricesTable(self.object)
        RequestConfig(self.request, paginate={'per_page': 20}).configure(price_table)
        return price_table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price_table'] = self.price_table()
        data_table = self.change_table()
        context['rising_table'] = data_table['rising_table']
        context['falling_table'] = data_table['falling_table']
        stock_name = self.object[0].stock.name
        context['price_data'] = self.get_price_data(stock_name)
        self.current_data(object=Stocks.objects.get(ticker=self.kwargs['ticker']), context=context)
        return context
