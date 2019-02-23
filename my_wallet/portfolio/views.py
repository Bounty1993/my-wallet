from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView, CreateView, DetailView
)
from .forms import NewPortfolioForm
from .models import Portfolio


class HomeView(TemplateView):
    template_name = 'portofolio/home.html'


class NewPortfolioView(CreateView):
    template_name = 'portfolio/new.html'
    form_class = NewPortfolioForm

    def get_context_date(self, **kwargs):
        context = super().get_context_date(**kwargs)
        profile = self.request.user
        context['num_portfolios'] = len(profile.portfolio.all())

    def get_initial(self):
        initial = super().get_initial()
        initial['profile'] = self.request.user
        return initial


class PortfolioDetails(DetailView):
    template_name = 'portfolio'
    model = Portfolio
