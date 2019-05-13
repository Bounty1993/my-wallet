from django.urls import include, path

from .views import (
    ArticlesView, CsvPrices, ExcelPrices, HistoryView, StockCreateView,
    StockDetailView, StocksListView,
)

app_name = 'stocks'
urlpatterns = [
    path('', StocksListView.as_view(), name='list'),
    path('detail/<ticker>/', StockDetailView.as_view(), name='detail'),
    path('new/', StockCreateView.as_view(), name='new'),
    path('articles/<ticker>/', ArticlesView.as_view(), name='articles'),
    path('history/<ticker>/', HistoryView.as_view(), name='history'),
    path('download-csv/<slug:ticker>/', CsvPrices.as_view(), name='download_csv'),
    path('download-xml/<slug:ticker>/', ExcelPrices.as_view(), name='download_xml'),
]
