from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView, CreateView, DetailView
)
from .forms import NewPortfolioForm
from .models import Portfolio, Asset
from my_wallet.profiles.models import Profile


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
        return redirect('portfolio:details')


class PortfolioDetails(DetailView):
    template_name = 'portfolio/details.html'
    model = Portfolio
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = Asset.objects.filter(portfolio=self.object)
        return context






