from django.urls import path, include
from .views import (HomeView, NewPortfolioView,
                   PortfolioDetails,
)

app_name = 'portfolioportfolio'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new/', NewPortfolioView.as_view(), name='new'),
    # path('<slug:ticker>/', PortfolioDetails.as_view(), name='details')
]

