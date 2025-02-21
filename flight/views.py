from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse
from .forms import PassengerForm
from .models import Flight, Passenger, FlightPassenger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


# Create your views here.
def index(request):
    return render(request, "flights/index.html",{
        "flights" : Flight.objects.all()
    })

def flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    passengers = flight.passengers.all()

    # Store the checked-in status for each passenger
    passenger_status = {
        passenger.id: flight.flightpassenger_set.get(passenger=passenger).checked_in for passenger in passengers
    }

    # Create a list of passenger full names
    booked_passenger_names = [f"{p.first} {p.last}" for p in passengers]

    return render(request, "flights/flight.html", {
        "flight": flight,
        "passengers": passengers,
        "passenger_status": passenger_status,
        "non_passengers": Passenger.objects.exclude(flights=flight).all(),
        "booked_passenger_names": booked_passenger_names,  # ✅ Pass formatted names
    })





def book(request, flight_id):
    if request.method == "POST":
        flight = get_object_or_404(Flight, pk=flight_id)

        if request.user.is_staff:
            # Staff selects a passenger from dropdown
            passenger_id = request.POST.get("passenger")
            if not passenger_id:
                return HttpResponseBadRequest("No passenger selected.")
            passenger = get_object_or_404(Passenger, pk=int(passenger_id))
        else:
            # Find passenger by first and last name matching the logged-in user
            passenger = get_object_or_404(Passenger, first=request.user.first_name, last=request.user.last_name)

        # Add the passenger to the flight
        passenger.flights.add(flight)

        return HttpResponseRedirect(reverse("flight", args=(flight.id,)))

    return HttpResponseBadRequest("Invalid request")



def remove(request, flight_id):
    if request.method == "POST":
        flight = get_object_or_404(Flight, pk=flight_id)

        if request.user.is_staff:
            # Staff removes a selected passenger
            passenger_id = request.POST.get("passenger")
            if not passenger_id:
                return HttpResponseBadRequest("No passenger selected.")
            passenger = get_object_or_404(Passenger, pk=int(passenger_id))
        else:
            # Normal user removes themselves
            passenger = get_object_or_404(Passenger, first=request.user.first_name, last=request.user.last_name)

        # Remove the passenger from the flight
        passenger.flights.remove(flight)

        # If your model has a checked-in field, reset it
        if hasattr(passenger, "checked_in"):
            passenger.checked_in = False
            passenger.save()

        return HttpResponseRedirect(reverse("flight", args=(flight.id,)))

    return HttpResponseBadRequest("Invalid request")

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
        flight.status = "Ready"
    elif flight.status == "Ready":
        flight.status = "Boarding"
    elif flight.status == "Boarding":
        flight.status = "Landed"
        flight.completed = True  # Mark flight as completed
    flight.save()

    return redirect("flight", flight_id=flight.id)

def start(request):

    current_time = datetime.now().strftime("%H:%M:%S")

    return render(request, 'flights/start_page.html', {
        'image_path': 'images/Aeroplane.jpg',
        'current_time': current_time
    })
