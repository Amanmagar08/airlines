from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:flight_id>", views.flight, name="flight"),
    path("check-in/<int:flight_id>/<int:passenger_id>/", views.check_in, name="check_in"),
    path("<int:flight_id>/book", views.book, name="book"),
    path("<int:flight_id>/remove", views.remove, name="remove"),
    path("create_passenger/", views.create_passenger, name = "create_passenger"),
    path('success/', views.success, name='success'),
    path("flight/<int:flight_id>/update_status/", views.update_flight_status, name="update_flight_status"),

]
