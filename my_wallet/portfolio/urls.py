from django.urls import path, include
from .views import (
    NewPortfolioView,
    PortfolioDetails,
)

app_name = 'portfolio'
urlpatterns = [
    path('new/', NewPortfolioView.as_view(), name='new'),
    path('details/<int:pk>/', PortfolioDetails.as_view(), name='details'),
]

