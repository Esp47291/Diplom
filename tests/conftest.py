import pytest
from rest_framework.test import APIClient

from accounts.models import User
from authors.models import Author
from books.models import Book
from loans.models import Loan


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def reader_user(db):
    return User.objects.create_user(
        username="reader1",
        email="reader1@example.com",
        password="testpass123",
        role=User.Role.READER,
    )


@pytest.fixture
def librarian_user(db):
    return User.objects.create_user(
        username="lib1",
        email="lib1@example.com",
        password="testpass123",
        role=User.Role.LIBRARIAN,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin1",
        email="admin1@example.com",
        password="testpass123",
    )


@pytest.fixture
def author(db):
    return Author.objects.create(
        first_name="Leo",
        last_name="Tolstoy",
        birth_year=1828,
    )


@pytest.fixture
def book(db, author):
    return Book.objects.create(
        title="War and Peace",
        author=author,
        genre="novel",
        isbn="9781234567890",
        publication_year=1869,
    )


@pytest.fixture
def auth_client(api_client, reader_user):
    api_client.force_authenticate(user=reader_user)
    return api_client


@pytest.fixture
def lib_client(api_client, librarian_user):
    api_client.force_authenticate(user=librarian_user)
    return api_client
