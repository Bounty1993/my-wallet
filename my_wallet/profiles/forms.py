from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, HTML, Row, Column, Fieldset, Field
from .models import Profile


class MyProfileCreationForm(UserCreationForm):

    class Meta:
        model = Profile
        fields = ('username', 'email', 'password1', 'password2', 'image')


class ProfileUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    HTML('<img class="profile-image card-img-top" src="{{profile.image.url}}" '
                         'alt="Profile picture">'),
                    Div(Field('image', css_class='form-control-file')),
                    css_class='col-sm-4',
                ),
                Column(
                    'first_name', 'last_name', 'email', css_class='col-sm-8',
                )
            ),
            Row(
                Field('address'),
                Field('city'),
                Field('zip_code')
            ),
            Submit('submit', 'Update my profile!')
        )
        self.fields['image'].label = ''

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'image')
