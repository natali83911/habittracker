from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Habit
from .paginators import HabitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операций над привычками пользователя.

    Реализует:
      - Получение, создание, обновление и удаление привычек текущего пользователя.
      - Отдельную публичную коллекцию привычек (action "public") для неаутентифицированных пользователей.
      - Поддержку индивидуальной пагинации и сериализации.
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_permissions(self):
        """
        Определяет права доступа для различных действий ViewSet.

        Для action "public" доступ открыт всем (AllowAny).
        Для остальных действий: только авторизованный пользователь,
        причём только владелец может редактировать (IsOwnerOrReadOnly).

        Returns:
            list: Список объектов-permission-classes.
        """
        if self.action == "public":
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Определяет queryset в зависимости от текущего действия.

        - "list": привычки только текущего пользователя.
        - "public": только публичные привычки всех пользователей.
        - остальные: только привычки текущего пользователя.

        Returns:
            QuerySet: выборка привычек для текущего действия.
        """
        user = self.request.user
        if self.action == "list":
            return Habit.objects.filter(user=user)
        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        Сохраняет новую привычку, автоматически назначая текущего пользователя владельцем.

        Args:
            serializer (HabitSerializer): сериализатор привычки для сохранения.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def public(self, request):
        queryset = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
