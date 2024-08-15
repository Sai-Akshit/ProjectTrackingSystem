from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("projects/", views.ProjectView.as_view(), name="projects"),
]