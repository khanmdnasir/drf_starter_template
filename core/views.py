# views/base_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from core.services import BaseService
from pydantic import ValidationError
from bson import ObjectId

T = TypeVar('T', bound=BaseModel)


class BaseView(Generic[T], APIView):
    model_class: Type[T] = None  # Pydantic model to be set in subclass
    service: BaseService = None  # Service to be set in subclass

    def post(self, request):
        try:
            # Validate request data using the Pydantic model
            pre_modify_data = self.service.pre_modification(request)
            model_instance = self.model_class(**pre_modify_data)
            # Use the service to insert data
            inserted_id = self.service.insert_one(model_instance)
            return Response({"message": "Resource created", "id": inserted_id}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            # Find a single document by id
            result = self.service.find_one({"_id": ObjectId(pk)})
            if result:
                return Response(result, status=status.HTTP_200_OK)
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Return all documents
            results = self.service.find_all({"user_id": request.user.id})
            return Response(results, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            # Validate and update document
            pre_modify_data = self.service.pre_modification(request)
            model_instance = self.model_class(**pre_modify_data)
            update_result = self.service.update_one({"_id": ObjectId(pk)}, model_instance)
            if update_result["modified_count"] > 1:
                return Response({"message": "Resource updated"}, status=status.HTTP_200_OK)
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(e.errors(), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        delete_result = self.service.delete_one({"_id": ObjectId(pk)})
        if delete_result["deleted_count"] > 1:
            return Response({"message": "Resource deleted"}, status=status.HTTP_200_OK)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
