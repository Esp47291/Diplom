import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_list_books(api_client, book):
    url = reverse("book-list")
    r = api_client.get(url)
    assert r.status_code == status.HTTP_200_OK
    titles = [row["title"] for row in r.data["results"]]
    assert book.title in titles


@pytest.mark.django_db
def test_search_books(api_client, book):
    url = reverse("book-list")
    r = api_client.get(url, {"search": "War"})
    assert r.status_code == status.HTTP_200_OK
    assert any(row["id"] == book.id for row in r.data["results"])


@pytest.mark.django_db
def test_create_book_authenticated_user(auth_client, author):
    url = reverse("book-list")
    r = auth_client.post(
        url,
        {
            "title": "Crime and Punishment",
            "author": author.id,
            "genre": "novel",
            "isbn": "",
            "publication_year": 1866,
        },
        format="json",
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_delete_book_forbidden_for_non_creator(api_client, author, reader_user, librarian_user):
    from books.models import Book
    from accounts.models import User

    creator = reader_user
    other = User.objects.create_user(
        username="reader2",
        email="reader2@example.com",
        password="testpass123",
        role=User.Role.READER,
    )
    b = Book.objects.create(title="To delete", author=author, genre="x", created_by=creator)

    api_client.force_authenticate(user=other)
    url = reverse("book-detail", kwargs={"pk": b.pk})
    r = api_client.delete(url)
    assert r.status_code == status.HTTP_403_FORBIDDEN
