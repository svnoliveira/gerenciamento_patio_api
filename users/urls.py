from django.urls import path
from .views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserCreateView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("register/", UserCreateView.as_view()),
    path("me/", MeView.as_view()),
    path("users/", UserListCreateView.as_view()),
    path("users/<int:user_id>/", UserRetrieveUpdateDestroyView.as_view()),
    path("login/", CookieTokenObtainPairView.as_view()),
    path("refresh/", CookieTokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("password-reset/", PasswordResetRequestView.as_view()),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view()),
]
