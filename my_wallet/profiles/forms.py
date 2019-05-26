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
        self.fields['password1'].help_text = 'Choose the wise one!'

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
            raise forms.ValidationError('That email is used')
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image', 'first_name', 'last_name', 'email',
                  'address', 'city', 'zip_code', 'description')
        widgets = {
            'description': forms.Textarea(
                attrs={'placeholder': 'Tell us something about yourself. Let other to get to know You!',
                       'rows': 5, 'col': 15}
            )
        }


class EmailUpdateForm(ProfileUpdateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column(Field('email', placeholder='Your private email'), css_class='col-md-8'),
                Column(Submit('submit', 'Update my email', css_class='mr-0'), css_class='col-md-4'),
            )
        )

    class Meta(ProfileUpdateForm.Meta):
        model = Profile
        fields = ('email', )


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('old_password', placeholder='Current Password'),
                    Field('new_password1', placeholder='New Password'),
                    Field('new_password2', placeholder='Repeat Password'),
                    css_class='col-sm-6',
                ),
                Column(
                    HTML("""<b>Care about security and follow below rules:</b>
                         <ul style="font-size: 14px">
                             <li>Your password can't be too similar to your other personal information.</li>
                             <li>Your password must contain at least 8 characters.</li>
                             <li>Your password can't be a commonly used password.</li>
                             <li>Your password can't be entirely numeric.</li>
                         </ul>"""
                         ),
                    css_class='col-sm-6',
                ),
            ),
            Row(
                Submit('submit', 'Update my profile!', css_class='btn btn-success mx-1'),
                Reset('reset', 'Reset values', css_class='btn btn-warning mx-1'),
                Button('cancel', 'Cancel', css_class='btn btn-danger mx-1'),
                css_class='d-flex justify-content-center',
            ),
        )
        self.fields['new_password1'].help_text = None


class ContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('subject', placeholder='Subject'),
            Field('message', placeholder='Ask about whatever you want'),
            Div(
                Submit('submit', 'Send', css_class='btn btn-success mx-1'),
                Reset('reset', 'Reset message', css_class='btn btn-warning mx-1'),
                Button('cancel', 'Cancel', css_class='btn btn-danger mx-1'),
                css_class='d-flex justify-content-center',
            ),

        )

    subject = forms.CharField(max_length=50)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'col': 15}))
