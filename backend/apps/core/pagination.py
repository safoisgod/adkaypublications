"""
Pagination classes for the API.
"""
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """
    Standard page-number pagination.
    Supports ?page=N and ?page_size=N (up to max 50).
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'current_page': {'type': 'integer'},
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'results': schema,
            },
        }


class SmallResultsPagination(StandardResultsPagination):
    """For endpoints needing smaller page sizes (e.g. featured items)."""
    page_size = 6
    max_page_size = 20


class LargeResultsPagination(StandardResultsPagination):
    """For search results or admin-facing lists."""
    page_size = 24
    max_page_size = 100
