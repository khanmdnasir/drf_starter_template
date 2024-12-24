from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from django.utils.encoding import force_str


class CustomException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."

    def __init__(self, status_code=None, detail=None, field=None):
        if status_code is not None:
            self.status_code = status_code
        if field is not None and detail is not None:
            self.detail = {field: force_str(detail)}
        elif detail is not None:
            self.detail = force_str(detail)
        else:
            self.detail = force_str(self.default_detail)


def handle_exceptions(func):
    """
    Decorator to wrap view logic with exception handling, allowing a serializer to be passed.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            errors = [
                {str(key): str(value[0])} for key, value in e.detail.items()
            ]
            return Response({"success": False, "error_type": "validation", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except CustomException as e:
            return Response(
                {
                    "success": False,
                    "error_type": "custom",
                    "errors": e.detail,
                },
                status=e.status_code,
            )
        except Exception as e:
            print(str(e))
            return Response(
                {
                    "success": False,
                    "error_type": "server",
                    "errors": "Something wrong!",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return wrapper
