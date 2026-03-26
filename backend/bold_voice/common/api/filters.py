from django_filters import rest_framework as filters

from rest_framework.filters import OrderingFilter


class DefaultOrderingFilter(OrderingFilter):

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view) or ['-id']

        """
        Sometimes if ordering field can result in ambiguous queryset.
        ex: queryset.order_by('-sort_order') what if two rows have same sort_order?

        To solve this ambiguity we append 'id' to the list,
        which is always unique. 
        """

        if 'id' not in ordering and '-id' not in ordering:
            ordering = ordering + ['-id']

        return queryset.order_by(*ordering)


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ModelChoiceInFilter(filters.BaseInFilter, filters.ModelChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('distinct', True)
        super().__init__(*args, **kwargs)


class ChoiceInFilter(filters.BaseInFilter, filters.ChoiceFilter):
    pass
