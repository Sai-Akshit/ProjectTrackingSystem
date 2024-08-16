from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("project/", views.ProjectView.as_view(), name="project"),
    path("scrum/", views.ScrumView.as_view(), name="scrum"),
    path("task/", views.TaskView.as_view(), name="task"),
]