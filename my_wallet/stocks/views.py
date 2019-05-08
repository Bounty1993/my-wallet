from django.views.generic import (
    ListView, DetailView,
    CreateView, TemplateView
)
from django.db.models import Q
from django.views import View
from django.core.cache import cache
from .models import Stocks, Prices, Dividends, Financial, PricesFilter
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
from openpyxl import Workbook


class BaseCsvExcelMixin:
    def _download_csv(self, model, headers, ticker):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{ticker}.csv"'

        writer = csv.writer(response)
        writer.writerow(headers)
        items = model.objects.filter(stock__ticker=ticker).values_list(*headers)

        for item in items:
            writer.writerow(item)
        return response

    def _download_xml(self, model, headers, ticker):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{ticker}.xls"'

        wb = Workbook()
        ws = wb.active
        ws.append(headers)
        items = model.objects.filter(stock__ticker=ticker).values_list(*headers)
        for item in items:
            ws.append(item)

        wb.save(response)
        return response


class CsvPrices(BaseCsvExcelMixin, View):
    def get(self, request, ticker):
        model = Prices
        headers = ['date_price', 'price', 'open', 'volume', 'change', 'percent_change']
        response = self._download_csv(model=model, headers=headers, ticker=ticker)
        return response


class ExcelPrices(BaseCsvExcelMixin, View):
    def get(self, request, ticker):
        model = Prices
        headers = ['date_price', 'price', 'open', 'volume', 'change', 'percent_change']
        response = self._download_xml(model=model, headers=headers, ticker=ticker)
        return response


class CurrentPriceMixin:

    def add_current_data(self, object, context):
        attributes = ['_price', '_day_change', '_percent_change']
        for attribute in attributes:
            ticker = self.object.ticker
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
    """
    Responsible for returning table with stocks with highest dividends.
    Use dividends_table method to get a table
    (e.g context["table"] = self.dividends_table())
    """

    def dividend_table(self):
        best_stocks = Stocks.highest_dividends()[:5]
        table = BestDividendsTable(best_stocks)
        RequestConfig(self.request).configure(table)
        return table


class StocksListView(BestWorstMixin, BestDividendsMixin, ListView):
    model = Stocks
    template_name = 'stocks/list.html'
    context_object_name = 'stocks'
    paginate_by = 10

    def get_queryset(self, *args):
        queryset = super().get_queryset(*args)
        q = self.request.GET.get('q')
        if q:
            return queryset.filter(
                Q(ticker__icontains=q) |
                Q(name__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        data_table = self.change_table()
        context['rising_table'] = data_table['rising_table']
        context['falling_table'] = data_table['falling_table']
        context['today'] = find_quote_day(today, 0, type='earlier')
        context['dividend_table'] = self.dividend_table()
        return context


class ChartMixin:

    earnings_names = [
        'total_revenue', 'gross_profit',
        'operating_income', 'net_income',
    ]
    balance_names = ['assets', 'liabilities']

    def get_earnings_data(self, earnings_names):
        finance_data = []
        for name in earnings_names:
            financial = self.object.financial.all()
            data = [float(field) for field in financial.values_list(name, flat=True) if field]
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

    def add_statement_data(self, context):
        context['finance_data'] = self.get_earnings_data(self.earnings_names)
        context['balance_data'] = self.get_balance_data(self.balance_names)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = DividendTable(self.object.dividends.all())
        RequestConfig(self.request, paginate={'per_page': 8}).configure(table)
        context['table'] = table
        context['last_dividend'] = Dividends.objects.filter(stock=self.object).latest('payment')
        self.add_current_data(self.object, context)
        self.add_statement_data(context)
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

    def add_articles(self, market, ticker, context):
        google_art = GoogleCrawler(market, ticker)
        context['google_news'] = google_art.get_data()
        yahoo_art = YahooCrawler(ticker)
        context['yahoo_news'] = yahoo_art.get_data()
        # bloomberg_art = BloombergCrawler(ticker)
        # context['bloomberg_news'] = bloomberg_art.get_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        market, ticker = self.market_ticker()
        self.add_articles(market, ticker, context)
        context['dividend_table'] = self.dividend_table()
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

    def price_table(self, context):
        f = PricesFilter(self.request.GET, queryset=self.object)
        context['filter'] = f
        price_table = PricesTable(f.qs)
        RequestConfig(self.request, paginate={'per_page': 20}).configure(price_table)
        context['price_table'] = price_table
        return price_table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.price_table(context)
        data_table = self.change_table()
        context['rising_table'] = data_table['rising_table']
        context['falling_table'] = data_table['falling_table']
        stock_name = self.object[0].stock.name
        context['price_data'] = self.get_price_data(stock_name)
        context['stock_ticker'] = self.kwargs.get('ticker')
        self.add_current_data(object=Stocks.objects.get(ticker=self.kwargs['ticker']), context=context)
        return context
