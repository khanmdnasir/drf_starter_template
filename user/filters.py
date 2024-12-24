from django_filters import rest_framework as filters
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.contrib.auth.models import Group


class UserFilter(filters.FilterSet):
    email = filters.CharFilter(field_name="email", lookup_expr="exact")
    name = filters.CharFilter(method="filter_by_name")
    is_active = filters.BooleanFilter(field_name="is_active", lookup_expr="exact")
    roles = filters.CharFilter(method="filter_by_roles")

    def filter_by_name(self, queryset, name, value):
        if value is None:
            return queryset

        return queryset.annotate(fullname=Concat("first_name", V(" "), "last_name")).filter(fullname__icontains=value)

    def filter_by_roles(self, queryset, name, value):
        selected_roles = value.split(",")
        groups = Group.objects.filter(name__in=selected_roles)
        return queryset.filter(groups__in=groups)
