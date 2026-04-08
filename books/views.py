from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets

from accounts.permissions import CanDeleteOwnBookOrStaff

from .filters import BookFilter
from .models import Book
from .serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список книг",
        description="Фильтры: название, жанр, автор, год. Поиск по названию и ISBN.",
    ),
    retrieve=extend_schema(summary="Карточка книги"),
    create=extend_schema(summary="Добавить книгу"),
    update=extend_schema(summary="Изменить книгу полностью"),
    partial_update=extend_schema(summary="Изменить книгу частично"),
    destroy=extend_schema(summary="Удалить книгу"),
)
@extend_schema(tags=["Книги"])
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    filterset_class = BookFilter
    search_fields = ("title", "genre", "isbn")
    ordering_fields = ("title", "genre", "publication_year", "created_at", "id")
    ordering = ["title"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), CanDeleteOwnBookOrStaff()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
