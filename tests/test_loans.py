import pytest
from django.urls import reverse
from rest_framework import status

from books.models import Book
from loans.models import Loan


@pytest.mark.django_db
def test_create_loan_librarian(lib_client, book, reader_user):
    url = reverse("loan-list")
    r = lib_client.post(
        url,
        {"book": book.id, "user": reader_user.id},
        format="json",
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert Loan.objects.filter(book=book, status=Loan.Status.ACTIVE).exists()


@pytest.mark.django_db
def test_reader_sees_only_own_loans(auth_client, book, reader_user, librarian_user):
    Loan.objects.create(book=book, user=reader_user, status=Loan.Status.ACTIVE)
    b2 = Book.objects.create(
        title="Other",
        author=book.author,
        genre="x",
    )
    Loan.objects.create(book=b2, user=librarian_user, status=Loan.Status.ACTIVE)

    url = reverse("loan-list")
    r = auth_client.get(url)
    assert r.status_code == status.HTTP_200_OK
    user_ids = {row["user"] for row in r.data["results"]}
    assert user_ids == {reader_user.id}


@pytest.mark.django_db
def test_double_active_loan_rejected(lib_client, book, reader_user):
    Loan.objects.create(book=book, user=reader_user, status=Loan.Status.ACTIVE)
    url = reverse("loan-list")
    r = lib_client.post(
        url,
        {"book": book.id, "user": reader_user.id},
        format="json",
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_return_loan(lib_client, book, reader_user):
    loan = Loan.objects.create(book=book, user=reader_user, status=Loan.Status.ACTIVE)
    url = reverse("loan-return-book", kwargs={"pk": loan.pk})
    r = lib_client.post(url)
    assert r.status_code == status.HTTP_200_OK
    loan.refresh_from_db()
    assert loan.status == Loan.Status.RETURNED
    assert loan.returned_at is not None
