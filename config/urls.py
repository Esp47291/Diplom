from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import (
    CabinetView,
    BookPageView,
    CatalogView,
    ContactsView,
    DiagramView,
    FAQView,
    GuideView,
    HealthCheckView,
    HomeView,
    LibrarianLoanExportView,
    SiteLoginView,
    SiteLogoutView,
    SiteRegisterView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("health/", HealthCheckView.as_view(), name="health"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("catalog/books/<int:pk>/", BookPageView.as_view(), name="book_page"),
    path("guide/", GuideView.as_view(), name="guide"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("diagram/", DiagramView.as_view(), name="diagram"),
    path("register/", SiteRegisterView.as_view(), name="site_register"),
    path("login/", SiteLoginView.as_view(), name="site_login"),
    path("logout/", SiteLogoutView.as_view(), name="site_logout"),
    path("cabinet/", CabinetView.as_view(), name="cabinet"),
    path(
        "cabinet/export-loans/",
        LibrarianLoanExportView.as_view(),
        name="cabinet_export_loans",
    ),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/authors/", include("authors.urls")),
    path("api/books/", include("books.urls")),
    path("api/loans/", include("loans.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
