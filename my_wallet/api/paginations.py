from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination,
)


class StandardPagePagination(PageNumberPagination):
    page_size = 5
