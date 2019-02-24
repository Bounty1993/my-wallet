from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views.generic import (
    TemplateView, CreateView, DetailView, View, ListView
)
from .forms import NewPortfolioForm, TransactionForm
from .models import Portfolio, Asset, Transaction, PastPortfolio


class NewPortfolioView(CreateView):
    template_name = 'portfolio/new.html'
    form_class = NewPortfolioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user
        context['profile'] = profile
        context['num_portfolios'] = len(profile.portfolio.all())
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['profile'] = self.request.user
        return initial

    def form_valid(self, form):
        portfolio = form.save(commit=False)
        portfolio.profile = self.request.user
        portfolio.save()
        return redirect('portfolio:details', pk=portfolio.pk)


class PortfolioDetails(DetailView):
    template_name = 'portfolio/details.html'
    model = Portfolio
    context_object_name = 'portfolio'

    def chart_data(self, assets):
        data = []
        for asset in assets:
            stocks_value = asset.stocks.price * asset.sum_number
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


class TransactionView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'portfolio/transaction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        portfolio = Portfolio.objects.get(pk=self.kwargs['pk'])
        data = (obj.stocks.ticker, obj.number)
        try:
            portfolio.verify_buy(*data)
        except ValueError:
            messages.warning(self.request, 'You do not have enough money!')
        else:
            obj.portfolio = portfolio
            obj.date = timezone.now()
            obj.kind = 'B'  #just for tests
            obj.get_price()
            obj.buy()
            obj.save()
        return redirect('portfolio:details', pk=self.kwargs['pk'])


class HistoryView(ListView):

    template_name = 'portfolio/history.html'
    model = PastPortfolio

    def get_queryset(self):
        portfolio_pk = self.kwargs.get('pk')
        portfolio = Portfolio.objects.get(pk=portfolio_pk)
        past_portfolio = PastPortfolio.objects.filter(portfolio=portfolio)
        past_portfolio.update_data()
        return past_portfolio

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        return context
