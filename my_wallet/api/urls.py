from django.urls import path, include
from .views import (
    PortfolioCreateAPIView,
    PortfolioListAPIView,
    PortfolioRetrieveUpdateDeleteAPIView,

    StocksListAPIView,
    StocksCreateAPIView,
    StocksRetrieveUpdateDestroyAPIView,
)

app_name = 'api'
urlpatterns = [
    path('portfolio/', PortfolioListAPIView.as_view(), name='portfolio'),
    path('portfolio/create', PortfolioCreateAPIView.as_view(), name='portfolio-create'),
    path('portfolio/<slug:name>/', PortfolioRetrieveUpdateDeleteAPIView.as_view(), name='portfolio_detail'),

    path('stocks/', StocksListAPIView.as_view(), name='stocks'),
    path('stocks/create', StocksCreateAPIView.as_view(), name='stocks_create'),
    path('stocks/<slug:ticker>/', StocksRetrieveUpdateDestroyAPIView.as_view(), name='stocks_details'),

]

