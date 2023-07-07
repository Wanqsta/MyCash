from os import login_tty
from django.urls import path
from .views import home, signup, login_view
from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path("", home, name="home"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout'),
]

