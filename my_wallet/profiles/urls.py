from django.contrib.auth import views
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView
)
from django.urls import include, path, re_path

from .views import (
    EditProfileView,
    MyPasswordChangeView,
    MyProfileCreationView,
    MyPasswordResetView,
    MyPasswordResetConfirmView,
    ProfileView,
    Contact,
)

app_name = 'profiles'

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('signup/', MyProfileCreationView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='profiles/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('edit/', EditProfileView.as_view(), name='edit'),
    path('password/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', MyPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('contact/', Contact.as_view(), name='contact'),

    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
]
