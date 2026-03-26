from rest_framework.pagination import BasePagination, PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class NoPagination(BasePagination):
    """A custom pagination class to disable pagination for a view."""

    def paginate_queryset(self, queryset, request, view=None):
        # NOTE: We must return the full queryset as a list instead of None.
        # Otherwise, `get_paginated_response` will not be called.
        return list(queryset)

    def get_paginated_response(self, data):
        # Constructs a standard API response for the un-paginated data.
        return Response({'results': data})

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'results': schema,
            },
        }
