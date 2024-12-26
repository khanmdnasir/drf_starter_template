from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from core.views import (
    BaseListPaginateView,
    BaseListView,
    BaseDetailView,
    BaseCreateView,
    BaseUpdateView,
    BaseUpdateStatusView
)
from core.exceptions import handle_exceptions
from user.services import UserService
from user.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from user.filters import UserFilter
from user.serializers import (
    LoginSerializer,
    UserSerializer,
    ProfileSerializer,
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
    BaseListPaginateView,
    BaseCreateView,
    BaseUpdateView,
    BaseUpdateStatusView
):
    queryset = User.objects.all().exclude(is_superuser=True)
    list_serializer_class = UserSerializer
    serializer_class = UserSerializer
    details_serializer_class = UserSerializer
    filterset_class = UserFilter

    def get_object(self, **kwargs):
        return self.queryset.get(id=kwargs.get("id"))

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        return super().get_permissions()


class ProfileUpdateView(BaseUpdateView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    details_serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, **kwargs):
        return self.request.user


class ChangePasswordView(views.APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class PasswordResetRequestView(BaseCreateView):
    serializer_class = PasswordResetRequestSerializer
    service_class = UserService
    permission_classes = [AllowAny]

    def process_post_request(self, serializer):
        """
        Handles password reset request logic.
        """
        self.service_class.send_password_reset_email(serializer.validated_data['email'])
        return {"success": True}


class PasswordResetView(BaseCreateView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]


class GroupView(
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseUpdateStatusView
):
    queryset = Group.objects.all()
    list_serializer_class = GroupListSerializer
    serializer_class = GroupSerializer
    details_serializer_class = GroupDetailsSerializer


class GroupDetailView(BaseDetailView):
    queryset = Group.objects.all()
    serializer_class = GroupDetailsSerializer


class PermissionView(views.APIView):
    queryset = ContentType.objects.all().exclude(model__in=['logentry', 'permission', 'session', 'contenttype'])

    def get(self, request):
        permission_list = []
        content_types = self.queryset.all()
        for i in content_types:
            groupPermission = Permission.objects.filter(content_type=i.id).values('name', 'codename')
            permission_list.append({i.model: groupPermission})

        return Response({"success": True, "data": permission_list}, status=status.HTTP_200_OK)
