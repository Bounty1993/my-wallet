from django.shortcuts import render, redirect
from django.views.generic import \
    TemplateView, CreateView
from .forms import AssetCreationFormset
import datetime
from .models import Portfolio
from django.contrib.auth.decorators import login_required

class HomeView(TemplateView):
    template_name = 'core/home.html'


class AssetCreateView(CreateView):
