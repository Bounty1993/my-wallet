from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.views.generic import (
    TemplateView, CreateView, DetailView, View, ListView
)
from django.db import transaction

from .forms import NewPortfolioForm, TransactionForm
from .models import Portfolio, Asset, Transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from my_wallet.stocks.models import Stocks


class NewPortfolioView(CreateView):
    template_name = 'portfolio/new.html'
    form_class = NewPortfolioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user
        context['profile'] = profile
        context['num_portfolios'] = profile.portfolio.count()
        return context

    def form_valid(self, form):
        portfolio = form.save(commit=False)
        portfolio.profile = self.request.user
        portfolio.cash = form.cleaned_data['beginning_cash']
        portfolio.save()
        return redirect('portfolio:details', pk=portfolio.pk)


class PortfolioDetails(LoginRequiredMixin, DetailView):
    template_name = 'portfolio/details.html'
    model = Portfolio
    context_object_name = 'portfolio'

    def chart_data(self, assets):
        data = []
        for asset in assets:
            stocks_value = Decimal(asset.stocks.current_price * asset.sum_number)
            percent = (stocks_value / self.object.total_value) * 100
            percent = float(round(percent, 2))
            asset_data = [asset.stocks.ticker, percent]
            data.append(asset_data)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        assets = Asset.objects.filter(portfolio=self.object)
        context['assets'] = assets
        context['data'] = self.chart_data(assets)
        return context


def transactions(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    kind = request.POST.get('kind') or 'B'
    if request.method == "POST":
        stock_id = request.POST.get('stocks')
        stock = Stocks.objects.get(id=stock_id)
        price = Stocks.get_current_price(ticker=stock.ticker)
        data = request.POST.copy()
        data['portfolio'] = portfolio.id
        data['kind'] = kind
        data['price'] = price
        form = TransactionForm(data)
        with transaction.atomic():
            if form.is_valid():
                obj = form.save()
                data_for_transaction = {
                    'number': obj.number,
                    'stock': obj.stocks,
                    'price': obj.price,
                }
                if obj.kind == 'B':
                    portfolio.buy(**data_for_transaction)
                else:
                    portfolio.sell(**data_for_transaction)

                return redirect('portfolio:details', pk=pk)
    else:
        form = TransactionForm()
    context = {'form': form}
    return render(request, 'portfolio/transaction.html', context)


class HistoryView(ListView):

    template_name = 'portfolio/history.html'
    #model = PastPortfolio

    def get_queryset(self):
        portfolio_pk = self.kwargs.get('pk')
        portfolio = Portfolio.objects.get(pk=portfolio_pk)
        past_portfolio = PastPortfolio.objects.filter(portfolio=portfolio)
        return past_portfolio

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        return context
