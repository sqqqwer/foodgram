from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGINATION_PAGE_SIZE


class LimitPageNumberPagination(PageNumberPagination):
    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = 'limit'
