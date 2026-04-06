from django.contrib import admin

from .models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ("first_name", "last_name")
    list_display = ("last_name", "first_name", "birth_year")
