from django.urls import path, include
from .views import (
    NewPortfolioView,
    PortfolioDetails,
    TransactionView,
    HistoryView,
)

app_name = 'portfolio'
urlpatterns = [
    path('new/', NewPortfolioView.as_view(), name='new'),
    path('details/<int:pk>/', PortfolioDetails.as_view(), name='details'),
    path('details/<int:pk>/transaction', TransactionView.as_view(), name='transaction'),
    path('details/<int:pk>/history', HistoryView.as_view(), name='history'),
]

