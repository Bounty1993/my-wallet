from django.urls import path, include
from .views import MyProfileCreation, ProfileView


app_name = 'profiles'
urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('signup/', MyProfileCreation.as_view(), name='signup'),
]