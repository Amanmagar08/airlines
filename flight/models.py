from django.db import models
import uuid

class Airport(models.Model):
    code = models.CharField(max_length=3)
    city = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.city} ({self.code})"

class Flight(models.Model):
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    duration = models.IntegerField()
    completed = models.BooleanField(default=False)  # Marks flight as completed
    status = models.CharField(
        max_length=20,
        choices=[
            ("Null", "Not Started"),
            ("ready", "Ready to Board"),
            ("boarding", "Boarding"),
            ("landed", "Landed")
        ],
        default="null"
    )

    def __str__(self):
        return f"{self.id}: {self.origin.city} to {self.destination.city} ({self.get_status_display()})"


class Passenger(models.Model):
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    flights = models.ManyToManyField(Flight, through="FlightPassenger", related_name="passengers")
    boarding_pass = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)

    def __str__(self):
        return f"{self.first} {self.last}"

class FlightPassenger(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    checked_in = models.BooleanField(default=False)

    class Meta:
        unique_together = ('passenger', 'flight')

    def __str__(self):
        return f"{self.passenger} on {self.flight}"