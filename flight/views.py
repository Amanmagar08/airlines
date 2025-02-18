from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse

from .models import Flight, Passenger

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return render(request, "flights/index.html",{
        "flights" : Flight.objects.all()
    })

def flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)

    return render(request, "flights/flight.html", {
        "flight": flight,
        "passengers": flight.passengers.all(),
        "non_passengers": Passenger.objects.exclude(flights=flight).all()  # Corrected query
    })


def book(request, flight_id):
    if request.method == "POST":
            flight = Flight.objects.get(pk = flight_id)
            passenger = Passenger.objects.get(pk = int(request.POST["passenger"]))
            passenger.flights.add(flight)
            return HttpResponseRedirect(reverse("flight", args=(flight.id,)))

def remove(request, flight_id):
    if request.method == "POST":
        flight = Flight.objects.get(pk=flight_id)
        passenger = Passenger.objects.get(pk=int(request.POST["passenger"]))
        passenger.flights.remove(flight)

        passenger.checked_in = False
        passenger.save()

        return HttpResponseRedirect(reverse("flight", args=(flight.id,)))

@csrf_exempt  # Only use this if you're not using CSRF protection in your AJAX request
def check_in(request, passenger_id):
    if request.method == "POST":
        try:
            passenger = Passenger.objects.get(id=passenger_id)
            passenger.checked_in = True
            passenger.save()
            return JsonResponse({"success": True})
        except Passenger.DoesNotExist:
            return JsonResponse({"success": False, "error": "Passenger not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})
