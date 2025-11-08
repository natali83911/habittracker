from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("habits/", include("habits.urls", namespace="habits")),
    path("users/", include("users.urls", namespace="users")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI с интерактивной документацией
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    # Альтернативно: Redoc UI
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
