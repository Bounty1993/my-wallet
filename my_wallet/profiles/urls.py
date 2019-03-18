from django.urls import path, include, re_path
from .views import (
    MyProfileCreationView,
    ProfileView,
    EditProfileView,
    MyPasswordChangeView,
    contact,
)
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'profiles'
urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('signup/', MyProfileCreationView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='profiles/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='profiles/logout.html'), name='logout'),
    path('edit/', EditProfileView.as_view(), name='edit'),
    path('password/', MyPasswordChangeView.as_view(), name='password_change'),
    path('contact/', contact, name='contact'),

    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
]