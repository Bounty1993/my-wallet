from django.urls import path, include
from .views import (
    StocksListView, StockDetailView,
    StockCreateView, ArticlesView,
    HistoryView, download_csv
)

app_name = 'stocks'
urlpatterns = [
    path('', StocksListView.as_view(), name='list'),
    path('detail/<slug:ticker>/', StockDetailView.as_view(), name='detail'),
    path('new/', StockCreateView.as_view(), name='new'),
    path('articles/<slug:ticker>/', ArticlesView.as_view(), name='articles'),
    path('history/<slug:ticker>/', HistoryView.as_view(), name='history'),
    path('download-csv/', download_csv, name='download-csv'),
]
