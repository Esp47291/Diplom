from django.db import models

from authors.models import Author
from accounts.models import User


class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
    )
    genre = models.CharField(max_length=100, db_index=True)
    isbn = models.CharField(max_length=20, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_books",
    )

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["genre"]),
            models.Index(fields=["title", "genre"]),
        ]

    def __str__(self) -> str:
        return self.title
