from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import LimitOffsetPagination
from core.exceptions import handle_exceptions
from core.views import (
    BaseListPaginateView,
    BaseListView,
    BaseDetailView,
    BaseCreateView,
    BaseUpdateView,
    BaseUpdateStatusView
)
from user.services import UserService, GroupService
from user.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from user.filters import UserFilter
from user.serializers import (
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    GroupSerializer,
    GroupListSerializer,
    GroupDetailsSerializer
)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    service_class = UserService

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.service_class.login(request, serializer.validated_data)
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)


class UserView(
    APIView,
    BaseListPaginateView,
    BaseCreateView,
    BaseUpdateView,
    BaseUpdateStatusView
):
    queryset = User.objects.all()
    list_serializer_class = UserListSerializer
    serializer_class = UserSerializer
    details_serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_class = UserFilter

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

class UserDetailView(BaseDetailView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileUpdateView(APIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer
    service_class = UserService

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service_class.send_password_reset_email(serializer.validated_data['email'])
        return Response({"success": True}, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class GroupView(
    APIView,
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseUpdateStatusView
):
    queryset = Group.objects.all().order_by("-id")
    list_serializer_class = GroupListSerializer
    serializer_class = GroupSerializer
    details_serializer_class = GroupListSerializer
    permission_classes = [DjangoModelPermissions]
    service_class = GroupService


class GroupDetailView(BaseDetailView):
    queryset = Group.objects.all()
    serializer_class = GroupDetailsSerializer
