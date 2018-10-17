from django.db import models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pdb

# Create your models here.
class Client(models.Model):
    gender_choices = (
        ("M", "Male"),
        ("F", "Female")
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    gender = models.CharField(max_length=1, choices=gender_choices)
    mobile_number = models.CharField(max_length=10)
    customer_id = models.IntegerField(default=None, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{} {} ({})".format(str(self.first_name), str(self.last_name), str(self.customer_id))

    def full_name(self):
        if self.gender == 'M':
            title = 'Mr.'
        else:
            title = 'Mrs.'
        return "{} {} {}".format(title, str(self.first_name), str(self.last_name))


class Policy(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    term_choices = (
        ("Q", "Quarterly"),
        ("H", "Half-Yearly"),
        ("A", "Annual")
    )
    premium_term = models.CharField(max_length=1, choices=term_choices, default='A')
    premium_amount = models.IntegerField()
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)

    def __str__(self):
        return str(self.number)

    def term_months(self):
        if self.premium_term == 'Q':
            return 3
        elif self.premium_term == 'H':
            return 6
        else:
            return 12

    def due_exists(self):
        return self.due_set.exists()

    def latest_due(self):
        if not self.due_exists():
            Due.objects.create(policy=self, due_date=self.start_date)
        return self.due_set.latest('due_date')

    def next_due_date(self):
        return self.latest_due().due_date

    def is_due_needed(self):
        if self.due_exists() is False:
            return True

        if all(due.premium_paid is True for due in self.due_set.all()) is True:
            return True

        if datetime.date(datetime.now()) > self.latest_due().due_date:
            return True

        return False

    def create_due(self):
        if self.is_due_needed() is False:
            return

        if self.due_exists() is False:
            due_date = self.start_date
        else:
            due_date = self.latest_due().due_date + relativedelta(months=self.term_months())

        if due_date > self.end_date:
            return

        due_date = date(due_date.year, due_date.month, 28)
        Due.objects.create(policy=self, due_date=due_date)
        self.create_due()

    def is_paid(self):
        return self.latest_due().paid

class Due(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    premium_paid = models.BooleanField(default=False)
    due_date = models.DateField()
    reminder_days_before = (-15, -2)

    def __str__(self):
        return "Policy({}) Due_date: {}".format(self.policy.number, self.due_date)

    def paid(self):
        if self.premium_paid == True:
            return "Paid"
        else:
            return "Not Paid"

    def grace_date(self):
        return self.due_date + relativedelta(months=1)

    def is_reminder_needed(self):
        if self.reminder_set.exists() is False:
            return True

        if self.reminder_set.count() >= len(self.reminder_days_before):
            return False

        if self.reminder_set.filter(reminder_sent__exact=False).count() > 0:
            return False

        return True

    def create_reminder(self):
        if self.is_reminder_needed() is False:
            return

        reminder_day = self.reminder_days_before[self.reminder_set.count()]
        reminder_date = self.due_date + relativedelta(days=reminder_day)
        client = self.policy.client
        Reminder.objects.create(due=self, reminder_date=reminder_date,
                                mobile_number=client.mobile_number, email=client.email)

class Reminder(models.Model):
    due = models.ForeignKey(Due, on_delete=models.CASCADE)
    reminder_sent = models.BooleanField(default=False)
    reminder_date = models.DateField()
    mobile_number = models.IntegerField()
    email = models.EmailField()

    def __str__(self):
        return 'Policy({}), Policy_Due_Date={}, Reminder_date={}'.format(self.due.policy.number,
                                                                         self.due.due_date, self.reminder_date)
