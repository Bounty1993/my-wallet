from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from my_wallet.stocks.models import Stocks, Dividends

admin.site.register(Profile)
admin.site.register(Stocks)
admin.site.register(Dividends)
