from django.urls import path, include
from .views import HomeView, create_asset

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new/', create_asset, name='new'),
]

