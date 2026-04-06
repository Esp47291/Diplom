import django_filters

from authors.models import Author
from .models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    genre = django_filters.CharFilter(lookup_expr="icontains")
    author = django_filters.ModelChoiceFilter(queryset=Author.objects.all())
    publication_year = django_filters.NumberFilter()
    publication_year__gte = django_filters.NumberFilter(
        field_name="publication_year",
        lookup_expr="gte",
    )
    publication_year__lte = django_filters.NumberFilter(
        field_name="publication_year",
        lookup_expr="lte",
    )

    class Meta:
        model = Book
        fields = ("title", "genre", "author", "publication_year")
