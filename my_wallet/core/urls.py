from django.urls import path, include
from .views import HomeView, AssetCreateView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new/', AssetCreateView.as_view(), name='new'),
]

