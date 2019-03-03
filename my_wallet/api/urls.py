from django.urls import path, include
from .views import (
    PortfolioCreateAPIView,
    PortfolioListAPIView,
    PortfolioRetrieveUpdateDeleteAPIView,

    StocksListAPIView,
    StocksCreateAPIView,
    StocksDetailAPIView,
    StocksUpdateAPIView,
    StocksDestroyAPIView,
)

app_name = 'api'
urlpatterns = [
    path('portfolio/', PortfolioListAPIView.as_view(), name='portfolio'),
    path('portfolio/create', PortfolioCreateAPIView.as_view(), name='portfolio-create'),
    path('portfolio/<slug:name>/', PortfolioRetrieveUpdateDeleteAPIView.as_view(), name='portfolio_detail'),

    path('stocks/', StocksListAPIView.as_view(), name='stocks'),
    path('stocks/create', StocksCreateAPIView.as_view(), name='stocks-create'),
    path('stocks/<slug:ticker>/', StocksDetailAPIView.as_view(), name='stocks-details'),
    path('stocks/<slug:ticker>/edit', StocksUpdateAPIView.as_view(), name='stocks-edit'),
    path('stocks/<slug:ticker>/delete', StocksDestroyAPIView.as_view(), name='stocks-delete'),
]

