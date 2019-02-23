from django.shortcuts import render, redirect
from django.views.generic import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import MyProfileCreationForm, ProfileUpdateForm
from .models import Profile


class MyProfileCreationView(CreateView):
    model = Profile
    template_name = 'profiles/signup.html'
    form_class = MyProfileCreationForm

    def form_valid(self, form):
        profile = form.save()
        return redirect(profile)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'profiles/profile.html'
    form_class = ProfileUpdateForm
    context_object_name = 'profile'

    def get_object(self):
        pk = self.request.user.pk
        return Profile.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['total_wealth'] = self.object.portfolio.total_value
        return context
