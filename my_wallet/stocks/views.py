import csv
import datetime

from django.shortcuts import get_object_or_404

from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from openpyxl import Workbook

from .crawler import GoogleCrawler, YahooCrawler
from .models import Dividends, Prices, Stocks, Financial
from .utils import find_quote_day


class CsvPrices(View):
    def get(self, request, ticker):
        prices = Prices.objects.filter(stock__ticker=ticker)
        if not prices.exists():
            raise Http404
        headers = ['date_price', 'price', 'open', 'volume', 'change', 'percent_change']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{ticker}.csv"'

        writer = csv.writer(response)
        writer.writerow(headers)
        items = prices.values_list(*headers)

        for item in items:
            writer.writerow(item)
        return response


class ExcelPrices(View):
    def get(self, request, ticker):
        prices = Prices.objects.filter(stock__ticker=ticker)
        if not prices.exists():
            raise Http404
        headers = ['date_price', 'price', 'open', 'volume', 'change', 'percent_change']
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{ticker}.xls"'

        wb = Workbook()
        ws = wb.active
        ws.append(headers)
        items = prices.values_list(*headers)
        for item in items:
            ws.append(item)

        wb.save(response)
        return response


class SideBarMixin:
    """
    Class is responsible for adding data to sidebar. Subclass needs
    to have self.kwargs['ticker']. Cache is used to get prices.
    """
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        attributes = ['_price', '_day_change', '_percent_change']
        ticker = self.kwargs.get('ticker')
        for attribute in attributes:
            result = cache.get(ticker + attribute, 'no data')
            context['stocks' + attribute] = result
        stock = Stocks.objects.get(ticker=ticker)
        context['side_stock'] = stock.name
        return context


class StocksListView(ListView):
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
        context['today'] = find_quote_day(today, 0, type='earlier')
        best_stocks = Stocks.objects.highest_dividends()[:5]
        context['dividend_stocks'] = best_stocks
        # sorted_stocks = sorted(Stocks.objects.all(), key=lambda stock: stock.perc_year_change)
        sorted_stocks = Prices.objects.year_change()
        context['rising'] = sorted_stocks[-5:]
        context['falling'] = sorted_stocks[:5]
        return context


class FinancialChartMixin:
    """
    Class is responsible for adding financial data to context.
    It is used by JavaScript to make charts. Subclass needs to have
    kwargs['ticker']
    """
    earnings_names = [
        'total_revenue', 'gross_profit',
        'operating_income', 'net_income',
    ]
    balance_names = ['assets', 'liabilities']

    def get_earnings_data(self, earnings_names):
        finance_data = []
        ticker = self.kwargs['ticker']
        financial = Financial.objects.filter(stock__ticker=ticker)
        for name in earnings_names:
            data = [float(field)/1e+6 for field in financial.values_list(name, flat=True) if field]
            finance_data.append({'name': name, 'data': data})
        return finance_data

    def get_balance_data(self, balance_names):
        balance_data = self.get_earnings_data(balance_names)
        return balance_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finance_data'] = self.get_earnings_data(self.earnings_names)
        context['balance_data'] = self.get_balance_data(self.balance_names)
        return context


class PriceChartMixin:
    object = None

    def get_num_seconds(self, date):
        epoch = datetime.date(1970, 1, 1)
        num_seconds = (date - epoch).total_seconds()*1000
        return int(num_seconds)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.object_list
        stock_name = queryset.first().stock.name
        instance = queryset.order_by('date_price')
        prices = [(self.get_num_seconds(field.date_price), float(field.price)) for field in instance]
        price_data = {'name': stock_name, 'prices': prices}
        context['price_data'] = price_data
        return context


class StockView(FinancialChartMixin, SideBarMixin, ListView):
    template_name = 'stocks/detail.html'
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'
    paginate_by = 10
    model = Stocks

    def get_queryset(self):
        ticker = self.kwargs['ticker']
        stock = get_object_or_404(Stocks, ticker=ticker)
        queryset = stock.dividends_summarize()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticker = self.kwargs.get('ticker')
        stock = Stocks.objects.get(ticker=ticker)
        context['stock'] = stock
        context['dividend_amount'] = stock.dividend_amount()
        context['dividend_rate'] = stock.dividend_rate()
        return context


class ArticlesView(SideBarMixin, TemplateView):
    template_name = 'stocks/articles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticker = self.kwargs.get('ticker')
        context['google_news'] = GoogleCrawler(ticker).get_data()
        context['yahoo_news'] = YahooCrawler(ticker).get_data()
        return context


class HistoryView(SideBarMixin, PriceChartMixin, ListView):
    template_name = 'stocks/history.html'
    slug_field = 'ticker'
    context_object_name = 'price_table'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_ticker'] = self.kwargs.get('ticker')
        return context

    def get_queryset(self):
        ticker = self.kwargs['ticker']
        queryset = Prices.objects.filter(stock__ticker=ticker)
        """
        q = self.request.GET.get('q', None)
        if q:
            date_price = datetime.datetime.strptime(q, '%y/%M/%Y')
            print(date_price)
            queryset = queryset.filter(date_price=date_price)
            return queryset
        """
        return queryset
