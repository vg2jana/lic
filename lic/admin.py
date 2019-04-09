from django.contrib import admin
from .forms import PolicyTypeForm

# Register your models here.

from .models import Client, Policy, Due, Reminder, PolicyType

class MyAdmin(admin.ModelAdmin):
    form = PolicyTypeForm


admin.site.register(Client)
admin.site.register(Policy)
admin.site.register(Due)
admin.site.register(Reminder)
admin.site.register(PolicyType, MyAdmin)