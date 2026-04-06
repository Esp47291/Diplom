from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import EmailTokenObtainPairView, RegisterView, SiteTokenRefreshView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", SiteTokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
