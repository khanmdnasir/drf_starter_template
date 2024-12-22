from rest_framework.permissions import AllowAny, DjangoModelPermissions
from user.models import User
from user.filters import UserFilter
from user.serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
)
from core.views import (
    BasePostView,
    BaseModelView
)


class LoginView(BasePostView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]


class UserView(BaseModelView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_class = UserFilter

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

