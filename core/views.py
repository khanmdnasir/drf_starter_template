from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from core.exceptions import handle_exceptions
from django.core.cache import cache
from hashlib import md5


class BaseViewMixin:
    queryset = None
    list_serializer_class = None
    filterset_class = None
    pagination_class = LimitOffsetPagination

    def get_queryset(self, request=None):
        """
        Returns a fresh queryset with optional filtering.
        """
        if self.queryset is None:
            raise AttributeError(f"{self.__class__.__name__} should include a `queryset` attribute.")

        # Use .all() to avoid reusing cached results
        queryset = self.queryset.all()

        # Apply filtering if request and filterset_class are available
        if request and self.filterset_class:
            filterset = self.filterset_class(request.GET, queryset=queryset)
            return filterset.qs if hasattr(filterset, 'qs') else queryset
        return queryset

    def paginate_queryset(self, request, queryset):
        """
        Paginates the queryset if a pagination class is defined.
        """
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        return paginator, paginated_queryset


class BaseListPaginateView(BaseViewMixin, APIView):
    @handle_exceptions
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests with optional filtering, pagination, and caching.
        """
        cache_key = f"{self.queryset.model.__name__.lower()}_list_{request.GET.urlencode()}"
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response({"success": True, "data": cached_response}, status=status.HTTP_200_OK)

        # Fresh queryset for every request
        queryset = self.get_queryset(request)
        paginator, paginated_queryset = self.paginate_queryset(request, queryset)
        serializer = self.list_serializer_class(paginated_queryset, many=True)

        # Cache the response
        response_data = serializer.data
        cache.set(cache_key, response_data, timeout=3600)  # Cache for 1 hour

        return paginator.get_paginated_response(response_data)


class BaseListView(BaseViewMixin, APIView):
    cache_timeout = 60 * 5  # Cache timeout in seconds (5 minutes by default)

    def generate_cache_key(self, request):
        """
        Generates a unique cache key based on the request path and query parameters.
        """
        query_string = request.META['QUERY_STRING']
        unique_key = f"{request.path}?{query_string}"
        return md5(unique_key.encode('utf-8')).hexdigest()

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests with optional caching and filtering.
        """
        # Generate a cache key
        cache_key = self.generate_cache_key(request)

        # Check if cached data exists
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)

        # Fresh data retrieval
        queryset = self.get_queryset(request)  # Fresh queryset
        serializer = self.list_serializer_class(queryset, many=True)
        response_data = {"success": True, "data": serializer.data}

        # Cache the response
        cache.set(cache_key, response_data, timeout=self.cache_timeout)

        return Response(response_data, status=status.HTTP_200_OK)


class BaseCreateView(APIView):
    queryset = None
    serializer_class = None
    details_serializer_class = None
    service_class = None

    def process_post_request(self, serializer):
        """
        Handles the core logic for creating or modifying an instance.
        """
        instance = serializer.save()

        # Invalidate related list caches
        cache_key = f"{self.queryset.model.__name__.lower()}_list_"
        cache.delete_pattern(f"{cache_key}*")  # Clear all related keys

        data = self.details_serializer_class(instance).data
        if self.service_class and hasattr(self.service_class, "post_modification"):
            return self.service_class.post_modification(data)
        return data

    @handle_exceptions
    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = self.process_post_request(serializer)
        return Response({"success": True, "data": response_data}, status=status.HTTP_201_CREATED)


class BaseUpdateView(APIView):
    queryset = None
    serializer_class = None
    details_serializer_class = None
    service_class = None

    def process_patch_request(self, serializer):
        """
        Handles the core logic for updating an instance.
        """
        updated_instance = serializer.save()

        # Invalidate cache
        self.invalidate_cache(updated_instance)

        data = self.details_serializer_class(updated_instance).data
        if self.service_class and hasattr(self.service_class, "post_modification"):
            return self.service_class.post_modification(data)
        return data

    def invalidate_cache(self, instance):
        """
        Invalidates the cache for related views or data.
        """
        model_name = self.queryset.model.__name__.lower()

        # Invalidate the detail view cache for this instance
        detail_cache_key = f"{model_name}_detail_{instance.id}"
        cache.delete(detail_cache_key)

        # Invalidate the list view cache
        list_cache_key = f"{model_name}_list_"
        cache.delete_pattern(f"{list_cache_key}*")

    def get_object(self, **kwargs):
        """
        Override this method in subclasses to return the specific object to update.
        """
        raise NotImplementedError("Subclasses must implement the `get_object` method.")

    @handle_exceptions
    def put(self, request, **kwargs):
        """
        Handles PUT requests to update an object.
        """
        instance = self.get_object(**kwargs)
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = self.process_patch_request(serializer)
        return Response({"success": True, "data": response_data}, status=status.HTTP_200_OK)

    @handle_exceptions
    def patch(self, request, **kwargs):
        """
        Handles PATCH requests to partially update an object.
        """
        instance = self.get_object(**kwargs)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        response_data = self.process_patch_request(serializer)
        return Response({"success": True, "data": response_data}, status=status.HTTP_200_OK)

class BaseDeleteView(APIView):
    queryset = None

    @handle_exceptions
    def delete(self, request, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        instance.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)


class BaseUpdateStatusView(APIView):
    queryset = None

    @handle_exceptions
    def patch(self, request, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        instance.is_active = not instance.is_active
        instance.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class BaseDetailView(APIView):
    queryset = None
    serializer_class = None

    @handle_exceptions
    def get(self, request, **kwargs):
        instance_id = kwargs.get("id")
        cache_key = f"{self.queryset.model.__name__.lower()}_{instance_id}"
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response({"success": True, "data": cached_response}, status=status.HTTP_200_OK)

        instance = self.queryset.get(id=instance_id)
        serializer = self.serializer_class(instance)
        data = serializer.data

        # Cache the response
        cache.set(cache_key, data, timeout=3600)  # Cache for 1 hour
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
