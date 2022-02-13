from pyexpat import model
from django.contrib import admin
from crm import models


admin.site.register(models.Customer)
admin.site.register(models.Contract)
admin.site.register(models.Event)
