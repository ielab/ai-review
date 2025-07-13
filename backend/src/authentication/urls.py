from django.urls import path

from authentication.views import *

urlpatterns = [
    path("request-otp", RequestOTPView.as_view()),
    path("validate-otp", ValidateOTPView.as_view()),
    path("reset-password", ResetPassword.as_view()),
    path("login", Login.as_view()),
    path("logout", Logout.as_view()),
    path("current", CurrentUser.as_view()),
]
