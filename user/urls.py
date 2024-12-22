from django.urls import path, include
from .views import *
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
router.register('users',UserViewSet)
# router.register('permission',PermissionViewSet)
# router.register('groups',GroupViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # path('user_role/',UserRoleApi.as_view()),
    # path('update_profile/',update_profile),
    # path('change_password/',change_password),
    path('auth/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]