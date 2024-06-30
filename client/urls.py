from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from client.views import (
    UserViewSet,
    LogoutView
)

app_name = "client"

user_detail = UserViewSet.as_view(
    actions={
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path(
        "register/",
        UserViewSet.as_view({"post": "create"}),
        name="register"
    ),
    path("me/", user_detail, name="me"),
    path(
        "me/schedule/",
        UserViewSet.as_view({"get": "schedule"}),
        name="schedule"
    ),
    path(
        "me/password/",
        UserViewSet.as_view({"put": "password", "patch": "password"}),
        name="password"
    ),
    path("users/", UserViewSet.as_view({"get": "list"}), name="users"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
