from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from .forms import NewPortfolioForm


class HomeView(TemplateView):
    template_name = 'core/home.html'


class NewPortfolioView(CreateView):
    template_name = 'portfolio/new.html'
    form_class = NewPortfolioForm

    def get_context_date(self, **kwargs):
        context = super().get_context_date(**kwargs)
        profile = self.request.user
        context['num_portfolios'] = len(profile.portfolio.all())