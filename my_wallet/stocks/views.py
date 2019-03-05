from django.views.generic import (
    ListView, DetailView,
    CreateView, TemplateView
)
from .models import Stocks, Prices
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
from .tables import PricesTable


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


class StockDetailView(DetailView):
    template_name = 'stocks/detail.html'
    model = Stocks
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prices = Prices.objects.filter(stock=self.object)
        table = PricesTable(prices)
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['prices'] = table
        year_change = self.object.year_change()
        context['percent'] = year_change['percent']
        context['currency'] = year_change['currency']
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
