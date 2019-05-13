from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView,
    RetrieveUpdateDestroyAPIView, UpdateAPIView,
)
from rest_framework.permissions import (
    IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.views import APIView

from my_wallet.portfolio.models import Portfolio
from my_wallet.stocks.models import Stocks
from my_wallet.stocks.utils import StockMaker

from .paginations import StandardPagePagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    PortfolioCreateSerializer, PortfolioListSerializer,
    PortfolioRetrieveUpdateDeleteSerializer, StocksCreateUpdateSerializer,
    StocksListSerializer, StocksRetrieveUpdateDeleteSerializer,
)


class PortfolioListAPIView(ListAPIView):
    serializer_class = PortfolioListSerializer
    permission_classes = [IsAuthenticated, ]

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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly,]

    lookup_field = 'name'


class StocksCreateAPIView(CreateAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StocksCreateUpdateSerializer
    permission_classes = [IsAdminUser, ]

    def perform_create(self, serializer):
        ticker = serializer.data['ticker']
        try:
            Stocks.objects.get(ticker=ticker)
        except Stocks.DoesNotExist:
            StockMaker(ticker=ticker)


class StocksRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StocksRetrieveUpdateDeleteSerializer

    lookup_field = 'ticker'


class StocksListAPIView(ListAPIView):
    queryset = Stocks.objects.all()
    serializer_class = StocksListSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = StandardPagePagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['ticker', 'name']
