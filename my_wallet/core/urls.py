from django.urls import path, include
from .views import HomeView, TransactionCreateView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new/', TransactionCreateView.as_view(), name='new'),
]

