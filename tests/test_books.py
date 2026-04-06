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
def test_create_book_librarian(lib_client, author):
    url = reverse("book-list")
    r = lib_client.post(
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
