from datetime import datetime
from decimal import Decimal

from django.http import Http404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DetailView, ListView, TemplateView, View, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from my_wallet.stocks.models import Stocks

from .forms import NewPortfolioForm, TransactionForm
from .models import Asset, Portfolio, Transaction


class NewPortfolioView(LoginRequiredMixin, CreateView):
    template_name = 'portfolio/new.html'
    form_class = NewPortfolioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_portfolios'] = self.request.user.portfolio.count()
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

    def get(self, request, *args, **kwargs):
        portfolio_id = self.kwargs['pk']
        portfolio = request.user.portfolio.filter(pk=portfolio_id)
        if portfolio.exists():
            return super().get(request, *args, **kwargs)
        else:
            raise Http404

    def chart_data(self, assets):
        data = []
        total_value = self.object.total_value
        for asset in assets:
            stocks_value = Decimal(asset.stocks.current_price * asset.sum_number)
            percent = (stocks_value / total_value) * 100
            percent = float(round(percent, 2))
            asset_data = [asset.stocks.ticker, percent]
            data.append(asset_data)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = self.object.asset.all().prefetch_related('stocks')
        context['assets'] = assets
        context['portfolio'] = self.object.get_summary()
        context['data'] = self.chart_data(assets)
        return context


def transactions(request, pk, kind):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    if kind not in ['buy', 'sell']:
        raise Http404
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

                if obj.kind == 'buy':
                    portfolio.buy(**data_for_transaction)
                elif obj.kind == 'sell':
                    portfolio.sell(**data_for_transaction)
                else:
                    raise ValueError('Typ transakcji jest błędny')

                return redirect('portfolio:details', pk=pk)
    else:
        form = TransactionForm()
        if kind == 'sell':
            possessed_stocks = portfolio.asset.prefetch_related('stocks')
            form.fields['stocks'].queryset = possessed_stocks
    context = {
        'form': form,
        'portfolio_pk': pk
    }
    return render(request, 'portfolio/transaction.html', context)


class PastTransactionsView(ListView):
    template_name = 'portfolio/past_transactions.html'
    model = Transaction
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        portfolio_id = self.kwargs['pk']
        return Transaction.objects.filter(portfolio_id=portfolio_id)

