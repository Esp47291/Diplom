import pytest
from django.urls import reverse
from rest_framework import status

from accounts.models import User


@pytest.mark.django_db
def test_register_creates_reader(api_client):
    url = reverse("register")
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "secretpass1",
        "password_confirm": "secretpass1",
    }
    r = api_client.post(url, payload, format="json")
    assert r.status_code == status.HTTP_201_CREATED
    u = User.objects.get(username="newuser")
    assert u.role == User.Role.READER


@pytest.mark.django_db
def test_register_password_mismatch(api_client):
    url = reverse("register")
    payload = {
        "username": "u2",
        "email": "u2@example.com",
        "password": "secretpass1",
        "password_confirm": "other",
    }
    r = api_client.post(url, payload, format="json")
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_jwt_obtain_pair(api_client, reader_user):
    url = reverse("token_obtain_pair")
    r = api_client.post(
        url,
        {"username": "reader1", "password": "testpass123"},
        format="json",
    )
    assert r.status_code == status.HTTP_200_OK
    assert "access" in r.data
    assert "refresh" in r.data


@pytest.mark.django_db
def test_me_endpoint(auth_client, reader_user):
    url = reverse("user-me")
    r = auth_client.get(url)
    assert r.status_code == status.HTTP_200_OK
    assert r.data["username"] == reader_user.username


@pytest.mark.django_db
def test_user_list_forbidden_for_reader(auth_client):
    url = reverse("user-list")
    r = auth_client.get(url)
    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_list_allowed_for_librarian(lib_client):
    url = reverse("user-list")
    r = lib_client.get(url)
    assert r.status_code == status.HTTP_200_OK
