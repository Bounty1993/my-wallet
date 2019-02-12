from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from .forms import MyProfileCreationForm

admin.site.register(Profile)
