from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from core.exceptions import handle_exceptions


class BaseListPaginateView:
    queryset = None
    list_serializer_class = None
    filterset_class = None
    pagination_class = LimitOffsetPagination

    def get_queryset(self, request):
        """
        Returns a filtered and paginated queryset.
        """
        if self.queryset is None:
            raise AttributeError(f"{self.__class__.__name__} should include a `queryset` attribute.")

        queryset = self.queryset
        if self.filterset_class:
            filterset = self.filterset_class(request.GET, queryset=queryset)
            return filterset.qs if hasattr(filterset, 'qs') else queryset
        return queryset

    def paginate_queryset(self,request, queryset):
        """
        Paginates the queryset if a pagination class is defined.
        """
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        return paginator, paginated_queryset

    @handle_exceptions
    def get(self, request, **kwargs):
        """
        Handles GET requests with optional filtering and pagination.
        """
        queryset = self.get_queryset(request)
        paginator, paginated_queryset = self.paginate_queryset(request, queryset)
        serializer = self.list_serializer_class(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class BaseListView:
    queryset = None
    list_serializer_class = None
    filterset_class = None

    def get_queryset(self, request):
        """
        Returns a filtered and paginated queryset.
        """
        if self.queryset is None:
            raise AttributeError(f"{self.__class__.__name__} should include a `queryset` attribute.")

        queryset = self.queryset
        if self.filterset_class:
            filterset = self.filterset_class(request.GET, queryset=queryset)
            return filterset.qs if hasattr(filterset, 'qs') else queryset
        return queryset

    @handle_exceptions
    def get(self, request, **kwargs):
        """
        Handles GET requests with optional filtering and pagination.
        """
        queryset = self.get_queryset(request)
        serializer = self.list_serializer_class(queryset, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class BaseCreateView:
    serializer_class = None
    details_serializer_class = None
    service_class = None

    def process_request(self, serializer):
        """
        Handles the core logic for processing post requests.
        """

        # Pre-modification
        if self.service_class and hasattr(self.service_class, 'pre_modification'):
            instance = self.service_class.pre_modification(serializer)
        else:
            # Save the object
            instance = serializer.save()

        data = self.details_serializer_class(instance).data

        # Post-modification
        if self.service_class and hasattr(self.service_class, 'post_modification'):
            return self.service_class.post_modification(data)
        else:
            return data

    @handle_exceptions
    def post(self, request, **kwargs):
        """
        Handles POST requests.
        """
        # Serializer Validation
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        response_data = self.process_request(serializer)
        return Response(
            {"success": True, "data": response_data},
            status=status.HTTP_201_CREATED
        )


class BaseUpdateView:
    queryset = None
    serializer_class = None
    details_serializer_class = None
    service_class = None

    def process_request(self, serializer):
        """
        Handles the core logic for processing post requests.
        """

        # Pre-modification
        if self.service_class and hasattr(self.service_class, 'pre_modification'):
            instance = self.service_class.pre_modification(serializer)
        else:
            # Save the object
            instance = serializer.save()

        data = self.details_serializer_class(instance).data

        # Post-modification
        if self.service_class and hasattr(self.service_class, 'post_modification'):
            return self.service_class.post_modification(data)
        else:
            return data

    @handle_exceptions
    def patch(self, request, **kwargs):
        """
        Handles PUT requests.
        """
        instance = self.queryset.get(id=kwargs.get("id"))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response_data = self.process_request(serializer)
        return Response(
            {"success": True, "data": response_data},
            status=status.HTTP_201_CREATED
        )


class BaseDeleteView:
    queryset = None

    @handle_exceptions
    def delete(self, request, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        instance.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)


class BaseUpdateStatusView:
    queryset = None

    @handle_exceptions
    def delete(self, request, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        instance.is_active = not instance.is_active
        instance.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class BaseDetailView(APIView):
    queryset = None
    serializer_class = None

    @handle_exceptions
    def get(self, request, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        serializer = self.serializer_class(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
