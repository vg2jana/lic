from django.core.management.base import BaseCommand
from insurance.models import Due, Client, Policy

class Command(BaseCommand):
    def handle(self, *args, **options):
        Due.objects.all().delete()
        Client.objects.all().delete()
        Policy.objects.all().delete()
