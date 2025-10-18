from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (DeactivateUserView, RegisterView, UserDetailView,
                    UserTelegramViewSet, UserViewSet)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"tg-profile", UserTelegramViewSet, basename="telegram-profile")


app_name = "users"

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path("user/", UserDetailView.as_view(), name="user_detail"),
    path("deactivate/", DeactivateUserView.as_view(), name="user-deactivate"),
]
