from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
    FormView,
)
from django.core.mail import send_mail
from .forms import (
    ContactForm,
    MyPasswordChangeForm,
    ProfileCreationForm,
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
        login(
            self.request,
            profile,
            backend='django.contrib.auth.backends.ModelBackend'
        )
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
        messages.success(self.request, 'Twoje hasło zostało pomyślnie zaaktualizowane')
        update_session_auth_hash(self.request, form.user)
        return redirect(reverse_lazy('profiles:profile'))


class MyPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('profiles:login')

    def form_valid(self, form):
        msg = """Na twój adres email został wysłany token służący do zmiany hasła
        Sprawdz czy dostałem wiadomość. Jeśli nie prosimy o kontakt"""
        messages.success(self.request, msg)
        return super().form_valid(form)


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('profiles:login')


class Contact(FormView):
    template_name = 'profiles/contact.html'
    form_class = ContactForm

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        content = form.cleaned_data['content']
        send_mail(
            subject=subject,
            message=content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER + '@gmail.com'],
            fail_silently=False,
        )
        msg = 'Dziękuję za kontakt. Odpowiem w ciągu 2 dni'
        messages.success(self.request, msg)
        return redirect(reverse_lazy('profiles:profile'))