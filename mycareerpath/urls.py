from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("error", views.error, name="error"),
    path("search", views.search, name="search"),
    path("saved_job", views.saved_job, name="saved_job"),
    path("tracker", views.tracker, name="tracker"),
    path("add", views.add, name="add"),

    # API routes
    path("save", views.save, name="save"),
    path("apply", views.apply, name="apply"),
    path("status", views.status, name="status"),
    path("remove_custom", views.remove_custom, name="remove_custom")
]