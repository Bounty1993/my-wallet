from django.views.generic import (
    ListView, DetailView,
    CreateView, TemplateView
)
from django.http import JsonResponse
from .models import Stocks, Prices, Dividends, Financial
import datetime
from django.utils import timezone
from .forms import NewStockForm
from .crawler import (
    GoogleCrawler,
    YahooCrawler,
    BloombergCrawler,
)
import json
from .utils import find_quote_day
from django_tables2 import RequestConfig
from .tables import DividendTable


class StocksListView(ListView):
    model = Stocks
    template_name = 'stocks/list.html'
    context_object_name = 'stocks'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = timezone.now().date()
        context['today'] = find_quote_day(date, 0, type='earlier')
        return context


class ChartMixin:

    def get_chart_data(self, earnings_names):
        finance_data = []
        for name in earnings_names:
            data = [float(field) for field in self.instance.values_list(name, flat=True)]
            finance_data.append({'name': name, 'data': data})
        return finance_data

    def get_balance_data(self, balance_names):
        balance_data = self.get_chart_data(balance_names)
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
        context['finance_data'] = self.get_chart_data(self.earnings_names)
        context['balance_data'] = self.get_balance_data(self.balance_names)
        return context


class StockDetailView(ChartMixin, DetailView):
    template_name = 'stocks/detail.html'
    model = Stocks
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    earnings_names = ['total_revenue', 'gross_profit', 'operating_income', 'net_income']
    balance_names = ['assets', 'liabilities']

    def get_context_data(self, **kwargs):
        self.instance = Financial.objects.filter(stock=self.object)
        context = super().get_context_data(**kwargs)
        last_dividend = Dividends.objects.latest('payment')
        table = DividendTable(Dividends.objects.filter(stock=self.object))
        RequestConfig(self.request, paginate={'per_page': 8}).configure(table)
        context['table'] = table
        # context['finance_data'] = self.get_chart_data(self.get_earnings_names())
        # context['balance_data'] = self.get_chart_data(self.get_balance_names())
        context['last_dividend'] = last_dividend
        return context


class StockCreateView(CreateView):
    template_name = 'stocks/new.html'
    form_class = NewStockForm

    def post(self, *args, **kwargs):
        try:
            self.object.get_past_data()
        except:
            print('hello')
        else:
            print('co tam')


class ArticlesView(TemplateView):
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
        self.process_context(market, ticker, context)
        return context
