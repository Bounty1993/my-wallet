from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, HTML, Row, Column, Fieldset, Field, Reset, Button
from crispy_forms.bootstrap import PrependedText
from .models import Profile


class MyProfileCreationForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ('username', 'email', 'password1', 'password2', 'image')


class ProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column(
                    HTML('<img class="profile-image card-img-top" src="{{profile.image.url}}" '
                         'alt="Profile picture">'),
                    Div(Field('image', css_class='form-control-file')),
                    css_class='col-sm-4',
                ),
                Column(
                    PrependedText('first_name', 'Your Name'),
                    PrependedText('last_name', 'Your Last Name'),
                    PrependedText('email', 'Your public email'),
                    PrependedText('address', 'Address'),
                    Row(
                        Column(
                            PrependedText('city', 'City'),
                            css_class='col-sm-6'
                        ),
                        Column(
                            PrependedText('zip_code', 'zip_code'),
                            css_class='col-sm-6',
                        )
                    ),
                    css_class='col-sm-8',
                )
            ),
            Row(
                Div(
                    'description',
                    css_class='col-sm-12'
                )
            ),
            Row(
                Submit('submit', 'Update my profile!', css_class='btn btn-success mx-1'),
                Reset('reset', 'Reset values', css_class='btn btn-warning mx-1'),
                Button('cancel', 'Cancel', css_class='btn btn-danger mx-1'),
                css_class='d-flex justify-content-center',
            ),
        )

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'image',
                  'address', 'city', 'zip_code', 'description')
        widgets = {
            'description': forms.Textarea(
                attrs={'placeholder': 'Tell us something about yourself. Let other to get to know You!',
                       'rows': 5, 'col': 15}
            )
        }


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
