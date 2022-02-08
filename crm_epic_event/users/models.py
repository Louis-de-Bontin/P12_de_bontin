from django.db import models
from django.contrib.auth.models import AbstractUser
from phone_field import PhoneField


class User(AbstractUser):
    MANAGER = 'MANAGER'
    SELLER = 'SELLER'
    SUPPORT = 'SUPPORT'
    
    ROLE_CHOICES = (
        (MANAGER, 'MANAGER'),
        (SELLER, 'SELLER'),
        (SUPPORT, 'SUPPORT')
    )

    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100)
    phone = PhoneField(null=True, blank=True, help_text='Phone number')
    # Il faudra que les manager soient admin
    role = models.CharField(choices=ROLE_CHOICES, default='MANAGER', max_length=10)
