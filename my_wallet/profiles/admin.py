from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from my_wallet.stocks.models import Dividends, Stocks

from .models import Profile

admin.site.register(Profile)
admin.site.register(Stocks)
admin.site.register(Dividends)
