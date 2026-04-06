from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsLibrarianOrAdmin
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


@extend_schema(
    tags=["Вход и регистрация"],
    summary="Регистрация читателя",
    description=(
        "Создаёт учётную запись с ролью «читатель». "
        "После регистрации получите токены через «Получить JWT-токены»."
    ),
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


@extend_schema(
    tags=["Вход и регистрация"],
    summary="Получить JWT (вход)",
    description="Укажите **username** и **password**. В ответе — access и refresh токены.",
)
class EmailTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    tags=["Вход и регистрация"],
    summary="Обновить access-токен",
    description="Отправьте действующий **refresh**, получите новый **access**.",
)
class SiteTokenRefreshView(TokenRefreshView):
    pass


@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей",
        description="Доступно библиотекарю и администратору.",
    ),
    retrieve=extend_schema(
        summary="Профиль пользователя",
        description="Читатель видит только себя; персонал — любого по id.",
    ),
)
@extend_schema(tags=["Пользователи"])
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        staff = user.is_superuser or user.role in (
            User.Role.LIBRARIAN,
            User.Role.ADMIN,
        )
        if staff:
            return User.objects.all().order_by("id")
        return User.objects.filter(pk=user.pk)

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]
        return [permissions.IsAuthenticated()]

    @extend_schema(
        summary="Мой профиль",
        description="Информация о текущем вошедшем пользователе (без id в URL).",
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
