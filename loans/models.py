from django.conf import settings
from django.db import models

from books.models import Book


class Loan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "На руках"
        RETURNED = "returned", "Возвращена"

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="loans",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["book", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.book_id} → {self.user_id} ({self.status})"
