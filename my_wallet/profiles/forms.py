from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, HTML, Row, Column, Fieldset, Field, Reset, Button
from crispy_forms.bootstrap import PrependedText
from .models import Profile


class ProfileCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Choose the wise one!'
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('username', placeholder='Username'),
            Field('password1', placeholder='Password'),
            Field('password2', placeholder='Password'),
            Fieldset(
                'Below data is not required',
                Field('email', placeholder='Email'),
                Field('first_name', placeholder='First Name'),
                Field('last_name', placeholder='Last Name'),
            ),
            Submit('submit', 'Create the account', css_class='half_btn btn btn-success'),
            Button('cancel', 'Resign', css_class='half_btn btn btn-danger')
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and Profile.objects.filter(email=email).exists():
            raise forms.ValidationError('That email is used')
        return email

    class Meta:
        model = Profile
        fields = ('username', 'password1', 'password2', 'email',
                  'first_name', 'last_name')

        help_texts = {
            'username': None,
            'password1': None,
        }


class ProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column(
                    Field('image'),
                    css_class='col-md-6 mb-0',
                ),
                Column(
                    Field('first_name', placeholder='First Name'),
                    Field('last_name', placeholder='Last Name'),
                    Field('email', placeholder='Public Email'),
                    css_class='col-md-6',
                ),
            ),
            Row(
                Column(Field('address', placeholder='Address')),
                Column(Field('city', placeholder='City')),
                Column(Field('zip_code', placeholder='Zip Code')),
                css_class='d-flex justify-content-around',
            ),
            Field('description'),
            Row(
                Submit('submit', 'Update my profile!', css_class='btn btn-success mx-1'),
                Reset('reset', 'Reset values', css_class='btn btn-warning mx-1'),
                Button('cancel', 'Cancel', css_class='btn btn-danger mx-1'),
                css_class='d-flex justify-content-center',
            ),
        )

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
