from django.db import models
from django.conf import settings
from phone_field import PhoneField
from datetime import datetime
from django.core import exceptions


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
    # Quand j'aurais fais l'autentification, il faudra que par défault ce soit l'utilisateur connecté si il est vendeur
    # ou que le champ soit requis si c'est un manager qui est connecté
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, 
        null=True, on_delete=models.SET_NULL, related_name='customer')

    def save(self, *args, **kwargs):
        if not self.compagny_name and not self.last_name:
                raise exceptions.FieldError(
                    'compagny_name and last_name can\'t be both empty.')
        self.date_updated = datetime.now()
        super().save(*args, **kwargs)
            

class Event(models.Model):
    name = models.CharField(max_length=25)
    location = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    date_event = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.date_updated = datetime.now()
        super().save(*args, **kwargs)
    

class Contract(models.Model):
    support = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL, related_name='in_charge')
    customer = models.ForeignKey(Customer, null=True,
        on_delete=models.SET_NULL, related_name='customer')
    event = models.OneToOneField(Event, null=True,
        on_delete=models.SET_NULL, related_name='event')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    signed = models.BooleanField(default=False)
    date_signed = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    due = models.FloatField(max_length=10)

    def save(self, *args, **kwargs):
        self.date_updated = datetime.now()
        super().save(*args, **kwargs)
