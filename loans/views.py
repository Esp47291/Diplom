from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User

from .filters import LoanFilter
from .models import Loan
from .serializers import LoanSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список выдач",
        description="Читатель видит только свои записи; библиотекарь — все.",
    ),
    retrieve=extend_schema(summary="Одна выдача"),
    create=extend_schema(
        summary="Выдать книгу",
        description="Укажите книгу и читателя. Нельзя выдать книгу, пока она уже на руках.",
    ),
    update=extend_schema(summary="Изменить выдачу полностью"),
    partial_update=extend_schema(summary="Изменить выдачу частично"),
    destroy=extend_schema(summary="Удалить запись выдачи"),
)
@extend_schema(tags=["Выдачи книг"])
class LoanViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LoanSerializer
    filterset_class = LoanFilter
    ordering_fields = ("issued_at", "due_date", "id")
    ordering = ["-issued_at"]

    def get_queryset(self):
        qs = Loan.objects.select_related("book", "book__author", "user").all()
        user = self.request.user
        if not user.is_authenticated:
            return Loan.objects.none()
        if user.is_superuser or user.role in (
            User.Role.LIBRARIAN,
            User.Role.ADMIN,
        ):
            return qs
        return qs.filter(user=user)

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    @extend_schema(
        summary="Вернуть книгу",
        description="Отмечает выдачу как возвращённую. Доступно владельцу выдачи или персоналу.",
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        loan = self.get_object()
        user = request.user
        staff = user.is_superuser or user.role in (User.Role.LIBRARIAN, User.Role.ADMIN)
        if not staff and loan.user_id != user.id:
            return Response(
                {"detail": "Нельзя вернуть чужую выдачу."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if loan.status == Loan.Status.RETURNED:
            return Response(
                {"detail": "Книга уже возвращена."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        loan.status = Loan.Status.RETURNED
        loan.returned_at = timezone.now()
        loan.save(update_fields=["status", "returned_at"])
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
