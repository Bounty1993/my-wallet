from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from .forms import (
    ContactForm, EmailUpdateForm, MyPasswordChangeForm, ProfileCreationForm,
    ProfileUpdateForm,
)
from .models import Profile
from my_wallet.portfolio.models import Portfolio


class MyProfileCreationView(CreateView):
    model = Profile
    template_name = 'profiles/signup.html'
    form_class = ProfileCreationForm

    def form_valid(self, form):
        profile = form.save()
        return redirect(profile)


class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'profiles/profile.html'
    context_object_name = 'portfolios'

    def get_queryset(self):
        profile = self.request.user
        return Portfolio.objects.filter(profile=profile)


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "profiles/edit_profile.html"
    form_class = ProfileUpdateForm

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'profiles/password_change.html'
    form_class = MyPasswordChangeForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your password was updated successfully!')
        update_session_auth_hash(self.request, form.user)
        return redirect(reverse_lazy('profiles:profile'))


def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)


def contact(request):
    if request.method == 'POST':
        print(request.POST)
        email_form = _get_form(request, EmailUpdateForm, prefix='email_pre')
        contact_form = _get_form(request, ContactForm, prefix='contact_pre')
        if email_form.is_bound and email_form.is_valid():
            print('I am email')
            pass
        elif contact_form.is_bound and contact_form.is_valid():
            print('I am here')
            messages.success(request, 'Thank you for your questions')
            return redirect(reverse_lazy('profiles:contact'))
        context = {'contact_form': contact_form, 'email_form': email_form}
        return render(request, 'profiles/contact.html', context)

    if request.method == 'GET':
        email_form = EmailUpdateForm(instance=request.user, prefix='email_pre')
        contact_form = ContactForm(prefix='contact_pre')
        context = {'contact_form': contact_form, 'email_form': email_form}
        return render(request, 'profiles/contact.html', context)
