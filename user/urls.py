from django.urls import path
from user.views import (
    LoginView,
    UserView,
    ProfileUpdateView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetView,
    GroupView,
    GroupDetailView,
    PermissionView
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('auth/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("users/", UserView.as_view(), name="users-create-list"),
    path("users/<int:id>/", UserView.as_view(), name="user-update-update_status"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path('profile/change-password/',ChangePasswordView.as_view(), name="change-password"),
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("groups/", GroupView.as_view(), name="groups-create-list"),
    path("groups/<int:id>/", GroupView.as_view(), name="group-update-update_status"),
    path("groups/<int:id>/details/", GroupDetailView.as_view(), name="group-details"),
    path("permissions/", PermissionView.as_view(), name="permissions-list"),
]