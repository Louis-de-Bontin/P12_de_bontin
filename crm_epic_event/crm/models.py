from django.db import models
from django.conf import settings
from phone_field import PhoneField
from datetime import datetime
from rest_framework.exceptions import PermissionDenied
import pytz


class Customer(models.Model):
    first_name = models.CharField(max_length=25, null=True, blank=True)
    last_name = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(max_length=100)
    phone = PhoneField(null=True, blank=True, help_text='Phone number')
    compagny_name = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    existing = models.BooleanField(default=False)
    notes = models.TextField(max_length=10000, blank=True, null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, 
        null=True, on_delete=models.SET_NULL, related_name='customer')

    def save(self, *args, **kwargs):
        try:
            self.check_fields()
        except PermissionDenied as e:
            raise e
        self.date_updated = datetime.now()
        super().save(*args, **kwargs)
    
    def check_fields(self):
        """
        A customer is identifiable with a name, a compagny, or both.
        Thats why at least of of those fiels is required.
        """
        if not self.compagny_name and not self.last_name:
            raise PermissionDenied(
                'compagny_name and last_name can\'t be both empty.')

    def __str__(self):
        if self.last_name and self.compagny_name:
            return str(self.first_name) + " " + str(self.last_name) + "; " + str(self.compagny_name)
        elif self.last_name:
            return str(self.first_name) + " " + str(self.last_name)
        return self.compagny_name
            

class Event(models.Model):
    name = models.CharField(max_length=25)
    location = models.CharField(max_length=255)
    finished = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    date_event = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.date_updated = datetime.now()
        self.date_event_not_passed()
        super().save(*args, **kwargs)
    
    def date_event_not_passed(self):
        """
        It is not possible to create an event with a passed date.
        """
        utc=pytz.UTC
        # if self.date_event < utc.localize(datetime.now()):
        #     raise PermissionDenied(
        #         'Event date can\'t be before event creation')
    
    def __str__(self):
        return self.name
    

class Contract(models.Model):
    """
    ATTENTION : si je modifie une signature, les 2 events restent
    Lors de la création d'un event, l'event n'est pas lié au contrat
    """
    support = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=False,
        on_delete=models.SET_NULL, related_name='in_charge')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL, related_name='writer')
    customer = models.ForeignKey(Customer, null=True,
        on_delete=models.SET_NULL, related_name='customer')
    event = models.OneToOneField(Event, null=True,
        on_delete=models.CASCADE, related_name='event')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    signed = models.BooleanField(default=False)
    date_signed = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    due = models.FloatField(max_length=10)
    payed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        A contract with a non existing customer update his status existing to True.
        """
        self.date_updated = datetime.now()
        self.update_customer_status()
        super().save(*args, **kwargs)
    
    def update_customer_status(self):
        self.date_updated = datetime.now()
        self.customer.existing = True
        self.customer.save()

    def sign(self, name_event, location_event, date_event):
        """
        Signing a contract automaticly create an event with the informations privided.
        """
        if self.signed == True:
            raise PermissionDenied('Contract already signed')

        self.signed = True
        self.date_signed = datetime.now()

        event = Event()
        event.name=name_event
        event.location=location_event
        event.date_event=datetime.strptime(date_event, '%d/%m/%Y %H:%M')
        event.save()

        self.event = event
        self.save()   
