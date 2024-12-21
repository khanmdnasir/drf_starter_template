from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.encoding import force_str


class CustomException(APIException): # type: ignore
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."

    def __init__(self, status_code=None, detail=None, field=None):
        if status_code is not None:
            self.status_code = status_code
        if field is not None and detail is not None:
            self.detail = {field: force_str(detail), "status": status_code}
        elif detail is not None:
            self.detail = {"detail": force_str(detail), "status": status_code}
        else:
            self.detail = {"detail": force_str(self.default_detail)}
