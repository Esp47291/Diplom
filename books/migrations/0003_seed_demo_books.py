from django.db import migrations


def seed_demo(apps, schema_editor):
    Author = apps.get_model("authors", "Author")
    Book = apps.get_model("books", "Book")

    if Book.objects.exists():
        return

    a1, _ = Author.objects.get_or_create(
        first_name="Лев",
        last_name="Толстой",
        defaults={
            "birth_year": 1828,
            "bio": "Русский писатель, один из крупнейших авторов мировой литературы.",
        },
    )
    a2, _ = Author.objects.get_or_create(
        first_name="Фёдор",
        last_name="Достоевский",
        defaults={
            "birth_year": 1821,
            "bio": "Русский писатель, классик, психологическая проза.",
        },
    )
    a3, _ = Author.objects.get_or_create(
        first_name="Михаил",
        last_name="Булгаков",
        defaults={
            "birth_year": 1891,
            "bio": "Русский писатель и драматург.",
        },
    )

    Book.objects.create(
        title="Война и мир",
        author=a1,
        genre="роман",
        isbn="",
        publication_year=1869,
    )
    Book.objects.create(
        title="Анна Каренина",
        author=a1,
        genre="роман",
        isbn="",
        publication_year=1877,
    )
    Book.objects.create(
        title="Преступление и наказание",
        author=a2,
        genre="роман",
        isbn="",
        publication_year=1866,
    )
    Book.objects.create(
        title="Идиот",
        author=a2,
        genre="роман",
        isbn="",
        publication_year=1869,
    )
    Book.objects.create(
        title="Мастер и Маргарита",
        author=a3,
        genre="роман",
        isbn="",
        publication_year=1967,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("authors", "0001_initial"),
        ("books", "0002_book_created_by"),
    ]

    operations = [
        migrations.RunPython(seed_demo, migrations.RunPython.noop),
    ]

