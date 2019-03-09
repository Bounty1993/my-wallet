from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,

)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)

from my_wallet.stocks.models import Stocks
from my_wallet.portfolio.models import Portfolio
from .serializers import (
    PortfolioCreateSerializer,
    PortfolioListSerializer,
    PortfolioRetrieveUpdateDeleteSerializer,

    StocksCreateUpdateSerializer,
    StocksListSerializer,
    StocksRetrieveUpdateDeleteSerializer,
)
from .paginations import StandardPagePagination


class PortfolioListAPIView(ListAPIView):
    serializer_class = PortfolioListSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        queryset = Portfolio.objects.filter(profile=self.request.user)
        return queryset


class PortfolioCreateAPIView(CreateAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioCreateSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user)


class PortfolioRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioRetrieveUpdateDeleteSerializer

    lookup_field = 'name'


class StocksCreateAPIView(CreateAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StocksCreateUpdateSerializer

    def perform_create(self, serializer):
        Stocks.get_stocks_with_data(ticker=serializer.data['ticker'])


class StocksRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StocksRetrieveUpdateDeleteSerializer

    lookup_field = 'ticker'


class StocksListAPIView(ListAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StocksListSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardPagePagination


