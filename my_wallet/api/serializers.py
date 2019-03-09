from rest_framework.serializers import (
    ModelSerializer,
    HyperlinkedIdentityField,
    SerializerMethodField,
)
from my_wallet.stocks.models import Stocks
from my_wallet.portfolio.models import Portfolio


class PortfolioListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='api:portfolio_detail',
        lookup_field='name'
    )
    profile = SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = (
            'url',
            'name',
            'profile',
            'cash',
            'created_at',
        )

    def get_profile(self, obj):
        return obj.profile.username


class PortfolioCreateSerializer(ModelSerializer):

    class Meta:
        model = Portfolio
        fields = (
            'name',
            'cash',
            'beginning_cash',
            'description',
            'is_visible',
        )


class PortfolioRetrieveUpdateDeleteSerializer(ModelSerializer):
    class Meta:
        model = Portfolio
        fields = (
            'name',
            'description',
            'is_visible',
        )


class StocksCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = Stocks
        fields = (
            'ticker',
        )


class StocksRetrieveUpdateDeleteSerializer(ModelSerializer):
    class Meta:
        model = Stocks
        fields = (
            'id',
            'name',
            'ticker',
        )


class StocksListSerializer(ModelSerializer):
    class Meta:
        model = Stocks
        fields = (
            'id',
            'name',
            'ticker',
        )
