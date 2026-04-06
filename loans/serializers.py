from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from books.serializers import BookSerializer

from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source="book", read_only=True)
    user_detail = UserPublicSerializer(source="user", read_only=True)

    class Meta:
        model = Loan
        fields = (
            "id",
            "book",
            "book_detail",
            "user",
            "user_detail",
            "issued_at",
            "due_date",
            "returned_at",
            "status",
        )
        read_only_fields = ("issued_at", "returned_at", "status")

    def validate(self, attrs):
        book = attrs.get("book") or (
            self.instance.book if self.instance else None
        )
        if self.instance is None and book:
            active = Loan.objects.filter(
                book=book,
                status=Loan.Status.ACTIVE,
            ).exists()
            if active:
                raise serializers.ValidationError(
                    {"book": "У этой книги уже есть активная выдача."}
                )
        return attrs
