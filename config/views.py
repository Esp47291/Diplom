import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from accounts.models import User
from loans.models import Loan
from books.models import Book

from .forms import ProfileEditForm, SiteRegisterForm


def _database_ok() -> bool:
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["service_ok"] = _database_ok()
        return ctx


class CatalogView(TemplateView):
    template_name = "pages/catalog.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        qs = Book.objects.select_related("author").all().order_by("title")
        if q:
            qs = qs.filter(title__icontains=q)
        ctx["q"] = q
        ctx["books"] = qs[:200]
        ctx["books_total"] = qs.count() if q else Book.objects.count()
        return ctx


class BookPageView(TemplateView):
    template_name = "pages/book_page.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book = Book.objects.select_related("author").get(pk=kwargs["pk"])
        ctx["book"] = book
        return ctx


class SiteRegisterView(FormView):
    template_name = "pages/register.html"
    form_class = SiteRegisterForm
    success_url = reverse_lazy("site_login")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Регистрация прошла успешно. Войдите под своей учётной записью.",
        )
        return super().form_valid(form)


class SiteLoginView(LoginView):
    template_name = "pages/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.setdefault("class", "site-input")
        return form


class SiteLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class CabinetView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "pages/cabinet.html"
    success_url = reverse_lazy("cabinet")
    login_url = reverse_lazy("site_login")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Данные профиля сохранены.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["role_label"] = dict(User.Role.choices).get(user.role, user.role)
        ctx["is_staff_portal"] = user.is_staff or user.role in (
            User.Role.LIBRARIAN,
            User.Role.ADMIN,
        )
        return ctx


class GuideView(TemplateView):
    template_name = "pages/guide.html"


class FAQView(TemplateView):
    template_name = "pages/faq.html"


class ContactsView(TemplateView):
    template_name = "pages/contacts.html"


class DiagramView(TemplateView):
    template_name = "pages/diagram.html"


class HealthCheckView(View):
    def get(self, request):
        ok = _database_ok()
        payload = {
            "service": "library-api",
            "status": "ok" if ok else "degraded",
            "database": "ok" if ok else "unavailable",
            "time": timezone.now().isoformat(),
        }
        return JsonResponse(payload, status=200 if ok else 503)


class LibrarianLoanExportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """CSV-выдача списка выдач (даты по дню выдачи)."""

    raise_exception = True

    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        return u.is_superuser or u.role in (
            User.Role.LIBRARIAN,
            User.Role.ADMIN,
        )

    def get(self, request):
        qs = Loan.objects.select_related("book", "book__author", "user").order_by(
            "-issued_at"
        )
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        df = parse_date(date_from) if date_from else None
        dt = parse_date(date_to) if date_to else None
        if df:
            qs = qs.filter(issued_at__date__gte=df)
        if dt:
            qs = qs.filter(issued_at__date__lte=dt)

        response = HttpResponse(
            content_type="text/csv; charset=utf-8",
        )
        fname = f"loans_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{fname}"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Книга",
                "Автор",
                "Читатель",
                "Email читателя",
                "Дата выдачи",
                "Срок возврата",
                "Дата возврата",
                "Статус",
            ]
        )
        for loan in qs:
            author = loan.book.author
            author_name = f"{author.first_name} {author.last_name}".strip()
            writer.writerow(
                [
                    loan.pk,
                    loan.book.title,
                    author_name,
                    loan.user.username,
                    loan.user.email or "",
                    timezone.localtime(loan.issued_at).strftime("%d.%m.%Y %H:%M"),
                    loan.due_date.strftime("%d.%m.%Y") if loan.due_date else "",
                    timezone.localtime(loan.returned_at).strftime("%d.%m.%Y %H:%M")
                    if loan.returned_at
                    else "",
                    loan.get_status_display(),
                ]
            )
        return response
