from .settings import *  # noqa: F403

# Достаточная длина ключа для JWT в тестах (избегаем InsecureKeyLengthWarning)
SECRET_KEY = "test-secret-key-not-for-production-use-32b+"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
