from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML, Button, Column, Div, Field, Fieldset, Layout, Reset, Row, Submit,
)

from .models import Profile


class ProfileCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Wybierz bezpieczne hasło'
        self.fields['password2'].help_text = 'Wpisz ponownie swoje hasło'

    class Meta:
        model = Profile
        fields = ('username', 'password1', 'password2', 'email',
                  'first_name', 'last_name')

        help_texts = {
            'username': None,
            'password1': None,
        }
        labels = {
            'username': 'Nazwa użytkownika',
            'password1': 'Hasło',
            'password2': 'Potwierdź hasło',
            'email': 'Adres email',
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and Profile.objects.filter(email=email).exists():
            raise forms.ValidationError('Wprowadzony email jest nieprawidłowy')
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image', 'first_name', 'last_name', 'email',
                  'address', 'city', 'zip_code', 'description')
        widgets = {
            'description': forms.Textarea(
                attrs={'placeholder': 'Powiedz nam coś o sobie. Pozwól innym się poznać!',
                       'rows': 5, 'col': 15}
            )
        }
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'email': 'Adres email',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        id = self.instance.id
        if email:
            is_taken = Profile.objects.exclude(id=id).filter(email=email)
            if is_taken:
                msg = 'Ten adres email jest już zajęty'
                raise forms.ValidationError(msg)
        return email


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=50, required=True)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'col': 15}), required=True)
    email = forms.EmailField(label='Twój email na który chcesz uzyskać odpowiedź', required=True)
