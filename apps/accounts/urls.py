from django.urls import path
from django.shortcuts import render

from apps.accounts.views import request_otp, verify_otp, logout_view

def index(request):
    return render(request, "index.html")

urlpatterns = [
    path("", index, name="index"),
    path("login/", request_otp, name="request_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("logout/", logout_view, name="logout"),
]