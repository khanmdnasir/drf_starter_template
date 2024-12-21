from django_filters import rest_framework as filters


class BaseFilter(filters.FilterSet):
    name = filters.CharFilter(method="filter_by_name")
    is_active = filters.BooleanFilter(method="filter_by_is_active")

    @staticmethod
    def filter_by_name(queryset, value):
        if value is None:
            return queryset

        return queryset.filter(name__icontains=value)

    @staticmethod
    def filter_by_is_active(queryset, value):
        if value is None:
            return queryset

        return queryset.filter(is_active=value)
