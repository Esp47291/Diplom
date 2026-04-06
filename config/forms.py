from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SiteRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "class": "site-input"}
        ),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "class": "site-input"}
        ),
        min_length=8,
    )

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {
            "username": "Имя пользователя",
            "email": "Email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("username", "email"):
            self.fields[name].widget.attrs.setdefault("class", "site-input")

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("password_confirm"):
            raise forms.ValidationError("Пароли не совпадают.")
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.READER
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    """Редактирование имени, фамилии и email в личном кабинете."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Электронная почта",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].widget.attrs.setdefault("class", "site-input")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("Укажите email.")
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Этот адрес уже используется другим пользователем.")
        return email
