from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from accounts.permissions import IsLibrarianOrAdmin

from .filters import AuthorFilter
from .models import Author
from .serializers import AuthorSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список авторов",
        description="Просмотр каталога. Поиск: параметры фильтра и поле поиска.",
    ),
    retrieve=extend_schema(summary="Карточка автора"),
    create=extend_schema(summary="Добавить автора"),
    update=extend_schema(summary="Изменить автора полностью"),
    partial_update=extend_schema(summary="Изменить автора частично"),
    destroy=extend_schema(summary="Удалить автора"),
)
@extend_schema(tags=["Авторы"])
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filterset_class = AuthorFilter
    search_fields = ("first_name", "last_name", "bio")
    ordering_fields = ("last_name", "first_name", "birth_year", "id")
    ordering = ["last_name", "first_name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return super().get_permissions()
        return [IsLibrarianOrAdmin()]
