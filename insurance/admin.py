from django.contrib import admin

# Register your models here.

from .models import Client, Policy, Due, Reminder, TemplateDue

admin.site.register(Client)
admin.site.register(Policy)
admin.site.register(Due)
admin.site.register(TemplateDue)
admin.site.register(Reminder)