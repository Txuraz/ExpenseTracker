from django.contrib import admin
from django.urls import path, include
from .views import Register, Login, UserView, Logout

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('users', UserView.as_view()),
    path('logout', Logout.as_view()),
]