import django_filters

from accounts.models import User
from books.models import Book
from .models import Loan


class LoanFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Loan.Status.choices)
    book = django_filters.ModelChoiceFilter(queryset=Book.objects.all())
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    issued_at__gte = django_filters.IsoDateTimeFilter(
        field_name="issued_at",
        lookup_expr="gte",
    )
    issued_at__lte = django_filters.IsoDateTimeFilter(
        field_name="issued_at",
        lookup_expr="lte",
    )

    class Meta:
        model = Loan
        fields = ("status", "book", "user")
