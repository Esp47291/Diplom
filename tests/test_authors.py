import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_list_authors_anonymous(api_client, author):
    url = reverse("author-list")
    r = api_client.get(url)
    assert r.status_code == status.HTTP_200_OK
    assert len(r.data["results"]) >= 1


@pytest.mark.django_db
def test_create_author_librarian(lib_client):
    url = reverse("author-list")
    r = lib_client.post(
        url,
        {
            "first_name": "Fyodor",
            "last_name": "Dostoevsky",
            "birth_year": 1821,
            "bio": "",
        },
        format="json",
    )
    assert r.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_author_forbidden_reader(auth_client):
    url = reverse("author-list")
    r = auth_client.post(
        url,
        {"first_name": "A", "last_name": "B", "bio": ""},
        format="json",
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_filter_authors_by_name(api_client, author):
    url = reverse("author-list")
    r = api_client.get(url, {"last_name__icontains": "Tolstoy"})
    assert r.status_code == status.HTTP_200_OK
    ids = [row["id"] for row in r.data["results"]]
    assert author.id in ids
