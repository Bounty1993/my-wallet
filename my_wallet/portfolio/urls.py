from django.urls import include, path

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
    path('<pk>/history', PastTransactionsView.as_view(), name='past_transactions'),
    path('<pk>/<kind>', transactions, name='transaction'),
]
