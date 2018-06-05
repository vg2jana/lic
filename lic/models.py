from django.db import models

# Create your models here.
class Client(models.Model):
    gender_choices = (
        ("M", "Male"),
        ("F", "Female")
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=250)
    gender = models.CharField(max_length=1, choices=gender_choices)
    mobile = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{} {}".format(str(self.first_name), str(self.last_name))

class Policy(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    policy_number = models.IntegerField()
    term_choices = (
        ("Q", "Quarterly"),
        ("H", "Half-Yearly"),
        ("A", "Annual")
    )
    premium_term = models.CharField(max_length=1, choices=term_choices)
    premium_amount = models.IntegerField()

    def __str__(self):
        return str(self.policy_number)