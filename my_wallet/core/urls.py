from django.urls import include, path

from .views import HomeView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
