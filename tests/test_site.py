import pytest
from django.urls import reverse

from loans.models import Loan


@pytest.mark.django_db
def test_health_ok(client):
    r = client.get(reverse("health"))
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


@pytest.mark.django_db
def test_guide_page(client):
    r = client.get(reverse("guide"))
    assert r.status_code == 200
    assert "три простых шага" in r.content.decode().lower()


@pytest.mark.django_db
def test_catalog_page(client, author):
    from books.models import Book

    Book.objects.create(title="Demo", author=author, genre="x")
    r = client.get(reverse("catalog"))
    assert r.status_code == 200
    assert "Demo" in r.content.decode()


@pytest.mark.django_db
def test_cabinet_requires_login(client):
    r = client.get(reverse("cabinet"))
    assert r.status_code == 302


@pytest.mark.django_db
def test_cabinet_profile_update(client, reader_user):
    client.force_login(reader_user)
    r = client.post(
        reverse("cabinet"),
        {
            "first_name": "Иван",
            "last_name": "Проверка",
            "email": reader_user.email,
        },
    )
    assert r.status_code == 302
    reader_user.refresh_from_db()
    assert reader_user.first_name == "Иван"
    assert reader_user.last_name == "Проверка"


@pytest.mark.django_db
def test_export_csv_librarian(client, librarian_user, book, reader_user):
    Loan.objects.create(book=book, user=reader_user, status=Loan.Status.ACTIVE)
    client.force_login(librarian_user)
    r = client.get(reverse("cabinet_export_loans"))
    assert r.status_code == 200
    assert "text/csv" in r["Content-Type"]
    body = r.content.decode("utf-8-sig")
    assert "Книга" in body
    assert book.title in body


@pytest.mark.django_db
def test_export_csv_forbidden_for_reader(client, reader_user):
    client.force_login(reader_user)
    r = client.get(reverse("cabinet_export_loans"))
    assert r.status_code == 403
