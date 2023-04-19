from django.urls import path

from .views import Login, Register

auth_urlpatterns = [
    path("user-login/", Login.as_view(), name="user-login"),
    path("user-register/", Register.as_view(), name="user-register"),
]
