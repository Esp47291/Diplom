from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        READER = "reader", "Читатель"
        LIBRARIAN = "librarian", "Библиотекарь"
        ADMIN = "admin", "Администратор"

    email = models.EmailField("email", unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
    )

    class Meta:
        db_table = "accounts_user"

    def __str__(self) -> str:
        return self.username
