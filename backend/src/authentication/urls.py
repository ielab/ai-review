from django.urls import path

from authentication.views import SignUp, Login, Logout, CurrentUser

urlpatterns = [
    path('sign-up', SignUp.as_view()),
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('current', CurrentUser.as_view()),
]
