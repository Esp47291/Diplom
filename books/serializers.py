from rest_framework import serializers

from authors.serializers import AuthorSerializer

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source="author", read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "author_detail",
            "genre",
            "isbn",
            "publication_year",
            "created_at",
        )
        read_only_fields = ("created_at",)
