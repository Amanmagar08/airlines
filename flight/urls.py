from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:flight_id>", views.flight, name="flight"),
    path("check-in/<int:passenger_id>/", views.check_in, name="check_in"),
    path("<int:flight_id>/book", views.book, name="book"),
    path("<int:flight_id>/remove", views.remove, name="remove")
]
