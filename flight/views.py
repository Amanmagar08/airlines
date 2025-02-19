from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PassengerForm
from .models import Flight, Passenger, FlightPassenger

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return render(request, "flights/index.html",{
        "flights" : Flight.objects.all()
    })

def flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    passengers = flight.passengers.all()
    passenger_status = {
        passenger.id: flight.flightpassenger_set.get(passenger=passenger).checked_in for passenger in passengers
    }
    return render(request, "flights/flight.html", {
        "flight": flight,
        "passengers": passengers,
        "passenger_status": passenger_status,
        "non_passengers": Passenger.objects.exclude(flights=flight).all()
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

@csrf_exempt
def check_in(request, passenger_id, flight_id):
    if request.method == "POST":
        try:
            flight_passenger = FlightPassenger.objects.get(passenger_id=passenger_id, flight_id=flight_id)
            flight_passenger.checked_in = True
            flight_passenger.save()
            return JsonResponse({"success": True})
        except FlightPassenger.DoesNotExist:
            return JsonResponse({"success": False, "error": "Passenger not found on this flight."})
    return JsonResponse({"success": False, "error": "Invalid request method."})

def create_passenger(request):
    if request.method == "POST":
        form = PassengerForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new passenger to the database
            return redirect('success')  # Redirect to a success page or flight detail page
    else:
        form = PassengerForm()
    return render(request, 'flights/create_passenger.html', {'form': form})


def success(request):
    return render(request, 'flights/success.html')

def update_flight_status(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    # Cycle through statuses
    if flight.status == "Null":
        flight.status = "ready"
    elif flight.status == "ready":
        flight.status = "boarding"
    elif flight.status == "boarding":
        flight.status = "landed"
        flight.completed = True  # Mark flight as completed
    flight.save()

    return redirect("flight", flight_id=flight.id)