from django.urls import path, include
from .views import (
    NewPortfolioView,
    PortfolioDetails,
    transactions,
    PastTransactionsView,
)

app_name = 'portfolio'
urlpatterns = [
    path('new/', NewPortfolioView.as_view(), name='new'),
    path('<pk>/', PortfolioDetails.as_view(), name='details'),
    path('<pk>/transaction', transactions, name='transaction'),
    path('<pk>/history', PastTransactionsView.as_view(), name='past_transactions'),
]

