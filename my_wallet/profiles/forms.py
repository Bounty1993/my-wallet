from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class MyProfileCreationForm(UserCreationForm):


    class Meta:
        model = Profile
        fields = ('username', 'email', 'password1', 'password2','image')