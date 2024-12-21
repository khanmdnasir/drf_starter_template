from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from core.exceptions import CustomException


class BaseView(APIView):
    @staticmethod
    def handle_exceptions(serializer=None):
        """
        Handle exceptions for the request lifecycle.
        """
        try:
            yield  # Execute the main logic
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "error_type": "validation",
                    "errors": [
                        {str(key): str(value[0])} for key, value in serializer.errors.items()
                    ] if serializer else str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except CustomException as e:
            return Response(
                {
                    "success": False,
                    "error_type": "custom",
                    "errors": e.detail
                },
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error_type": "server",
                    "errors": "Server error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BaseModelView(BaseView):
    queryset = None
    serializer_class = None
    service_class = None
    filterset_class = None
    pagination_class = LimitOffsetPagination

    def get_queryset(self, request):
        """
        Returns a filtered and paginated queryset.
        """
        filterset = self.filterset_class(request.GET, queryset=self.queryset) if self.filterset_class else self.queryset
        return filterset.qs if hasattr(filterset, 'qs') else self.queryset

    def paginate_queryset(self, queryset, request):
        """
        Paginates the queryset if a pagination class is defined.
        """
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        return paginator, paginated_queryset

    def get(self, request, **kwargs):
        """
        Handles GET requests with optional filtering and pagination.
        """
        with self.handle_exceptions():
            queryset = self.get_queryset(request)
            if self.pagination_class:
                paginator, paginated_queryset = self.paginate_queryset(queryset, request)
                serializer = self.serializer_class(paginated_queryset, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.serializer_class(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def process_post_request(self, request):
        """
        Handles the core logic for processing post requests.
        """
        # Pre-modification
        data = self.service_class.pre_modification(request)

        # Serializer Validation
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the object
        serializer.save()

        # Post-modification
        return self.service_class.post_modification(serializer.data)

    def post(self, request, **kwargs):
        """
        Handles POST requests.
        """
        with self.handle_exceptions():
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

    def patch(self, request, **kwargs):
        """
        Handles PUT requests.
        """
        with self.handle_exceptions():
            instance = self.queryset.get(id=kwargs.get("id"))
            response_data = self.process_patch_request(instance, request)
            return Response(
                {"success": True, "data": response_data},
                status=status.HTTP_201_CREATED
            )

    def delete(self, request, **kwargs):
        with self.handle_exceptions():
            instance = self.queryset.get(id=kwargs.get("id"))
            instance.delete()
            return Response({"success": True}, status=status.HTTP_200_OK)


class BaseDetailView(BaseView):
    queryset = None
    serializer_class = None

    def get(self, request, **kwargs):
        with self.handle_exceptions():
            instance = self.queryset.get(id=kwargs.get("id"))
            serializer = self.serializer_class(instance)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class BasePostView(BaseView):
    queryset = None
    serializer_class = None
    service_class = None

    def process_post_request(self, request):
        """
        Handles the core logic for processing post requests.
        """
        # Pre-modification
        data = self.service_class.pre_modification(request)

        # Serializer Validation
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the object
        serializer.save()

        # Post-modification
        return self.service_class.post_modification(serializer.data)

    def post(self, request, **kwargs):
        with self.handle_exceptions():
            response_data = self.process_post_request(request)
            return Response(
                {"success": True, "data": response_data},
                status=status.HTTP_201_CREATED
            )


class BaseGetView(BaseView):
    queryset = None
    service_class = None

    def get(self, request, **kwargs):
        with self.handle_exceptions():
            data = self.service_class.get(request, **kwargs)
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
