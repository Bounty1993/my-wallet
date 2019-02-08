from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import MyProfileCreationForm
from .models import Profile


class MyProfileCreation(CreateView):
    model = Profile
    template_name = 'profiles/signup.html'
    form_class = MyProfileCreationForm


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'

