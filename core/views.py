from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from core.exceptions import handle_exceptions


class BaseModelView(APIView):
    queryset = None
    serializer_class = None
    service_class = None
    filterset_class = None
    pagination_class = None

    def get_queryset(self):
        """
        Returns a filtered and paginated queryset.
        """
        if self.queryset is None:
            raise AttributeError(f"{self.__class__.__name__} should include a `queryset` attribute.")

        queryset = self.queryset
        if self.filterset_class:
            filterset = self.filterset_class(self.request.GET, queryset=queryset)
            return filterset.qs if hasattr(filterset, 'qs') else queryset
        return queryset

    def paginate_queryset(self, queryset):
        """
        Paginates the queryset if a pagination class is defined.
        """
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, self.request)
        return paginator, paginated_queryset

    @handle_exceptions
    def get(self, request, **kwargs):
        """
        Handles GET requests with optional filtering and pagination.
        """
        queryset = self.get_queryset()
        if self.pagination_class:
            paginator, paginated_queryset = self.paginate_queryset(queryset)
            serializer = self.serializer_class(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def process_post_request(self, request):
        """
        Handles the core logic for processing post requests.
        """
        # Pre-modification
        if self.service_class and hasattr(self.service_class, 'pre_modification'):
            data = self.service_class.pre_modification(request)
        else:
            data = request.data

        # Serializer Validation
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the object
        serializer.save()

        # Post-modification
        if self.service_class and hasattr(self.service_class, 'post_modification'):
            return self.service_class.post_modification(serializer.data)
        else:
            return serializer.data

    @handle_exceptions
    def post(self, request, **kwargs):
        """
        Handles POST requests.
        """
        response_data = self.process_post_request(request)
        return Response(
            {"success": True, "data": response_data},
            status=status.HTTP_201_CREATED
        )

    def process_patch_request(self, instance, request):
        """
        Handles the core logic for processing post requests.
        """
        # Serializer Validation
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Save the object
        serializer.save()

        # Post-modification
        return serializer.data

    @handle_exceptions
    def patch(self, request, **kwargs):
        """
        Handles PUT requests.
        """
        instance = self.queryset.get(id=kwargs.get("id"))
        response_data = self.process_patch_request(instance, request)
        return Response(
            {"success": True, "data": response_data},
            status=status.HTTP_201_CREATED
        )

    @handle_exceptions
    def delete(self, request, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        instance.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='update-status')
    @handle_exceptions
    def update_status(self, request, pk):
        instance = self.queryset.get(id=pk)
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


class BasePostView(APIView):
    queryset = None
    serializer_class = None
    service_class = None

    def process_post_request(self, request):
        """
        Handles the core logic for processing post requests.
        """
        # Pre-modification
        if self.service_class and hasattr(self.service_class, 'pre_modification'):
            data = self.service_class.pre_modification(request)
        else:
            data = request.data

        # Serializer Validation
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the object
        serializer.save()

        # Post-modification
        if self.service_class and hasattr(self.service_class, 'post_modification'):
            return self.service_class.post_modification(serializer.data)
        else:
            return serializer.data

    @handle_exceptions
    def post(self, request, **kwargs):
        response_data = self.process_post_request(request)
        return Response(
            {"success": True, "data": response_data},
            status=status.HTTP_200_OK
        )


class BaseGetView(APIView):
    queryset = None
    service_class = None

    @handle_exceptions
    def get(self, request, **kwargs):
        data = self.service_class.get(request, **kwargs)
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
