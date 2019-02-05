from django.urls import path, include
from .views import MyProfileCreation

app_name = 'profiles'
urlpatterns = [
    path('signup/', MyProfileCreation.as_view(), name='signup'),
]
