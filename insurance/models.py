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
            title = 'Ms.'
        return "{} {} {}".format(title, str(self.first_name), str(self.last_name))


class TemplateDue(models.Model):
    term_choices = (
        ("Q", "Quarterly"),
        ("H", "Half-Yearly"),
        ("A", "Annual")
    )
    term = models.CharField(max_length=1, choices=term_choices, default='A')
    month_choices = (
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    )
    month = models.IntegerField(choices=month_choices, default=1)
    reminder_days_before = models.CharField(max_length=200, default="2,15")

    def days_to_list(self):
        days = []
        for i in self.reminder_days_before.split(','):
            days.append(int(i.strip()))

        return sorted(days, reverse=True)

    def months_per_year(self):
        if self.term == 'A':
            months = [self.month,]
        elif self.term == 'H':
            months = [self.month, self.month + 6]
        else:
            months = [self.month, self.month + 3, self.month + 6, self.month + 9]

        return [m for m in months if m <= 12]

    def __str__(self):
        term = self.get_term_display()
        months = []
        for m in self.months_per_year():
            months.append(self.month_choices[m-1][1])
        return "%s: %s: %s" % (term, ", ".join(months), self.reminder_days_before)


class Policy(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    # term_choices = (
    #     ("Q", "Quarterly"),
    #     ("H", "Half-Yearly"),
    #     ("A", "Annual")
    # )
    # premium_term = models.CharField(max_length=1, choices=term_choices, default='A')
    premium_term = models.OneToOneField(TemplateDue, on_delete=models.CASCADE)
    premium_amount = models.IntegerField()
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=datetime.now)
    added_date = models.DateField(default=datetime.now)

    def __str__(self):
        return str(self.number)

    def term_months(self):
        if self.premium_term.term == 'Q':
            return 3
        elif self.premium_term.term == 'H':
            return 6
        else:
            return 12

    def due_exists(self):
        return self.due_set.exists()

    def latest_due(self):
        # if not self.due_exists():
        #     self.create_due()
        return self.due_set.latest('due_date')

    def next_due_date(self):
        return self.latest_due().due_date

    def is_due_needed(self):
        if self.due_exists() is False:
            return True

        if all(due.premium_paid is True for due in self.due_set.all()) is True:
            return True

        if self.latest_due().due_date.month >= date.today().month:
            return False

        if datetime.date(datetime.now()) > self.latest_due().due_date:
            return True

        return False

    def create_due(self):
        if self.is_due_needed() is False:
            return

        due_date = None
        months = self.premium_term.months_per_year()
        for m in months:
            now = date.today()
            if m >= now.month:
                if self.due_exists() is True:
                    if self.latest_due().due_date.month != m:
                        due_date = date(now.year, now.month, 28)
                else:
                    due_date = date(now.year, m, 28)
                break
        # else:
        #     due_date = self.latest_due().due_date + relativedelta(months=self.term_months())
        #     due_date = date(due_date.year, due_date.month, 28)

        if due_date is None or due_date > self.end_date:
            return

        # premium_paid = False
        # if due_date < self.added_date:
        #     premium_paid = True
        Due.objects.create(policy=self, due_date=due_date)
        # self.create_due()

    def is_paid(self):
        return self.latest_due().paid


class Due(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    premium_paid = models.BooleanField(default=False)
    due_date = models.DateField()
    # reminder_days_before = (-15, -2)

    def __str__(self):
        return "Policy({}) Due_date: {}".format(self.policy.number, self.due_date)

    def paid(self):
        if self.premium_paid is True:
            return "Paid"
        else:
            return "Not Paid"

    def grace_date(self):
        grace_date = self.due_date + relativedelta(months=1)
        return grace_date.strftime('%d/%m/%Y')

    def due_date_formatted(self):
        return self.due_date.strftime('%d/%m/%Y')

    def next_reminder(self):
        return self.reminder_set.latest('reminder_date').reminder_date.strftime('%d/%m/%Y')

    def is_reminder_needed(self):
        # Premium already paid
        if self.premium_paid is True:
            return False

        # No history of reminders
        if self.reminder_set.exists() is False:
            return True

        # No of reminders equals reminders needed
        if self.reminder_set.count() >= len(self.policy.premium_term.days_to_list()):
            return False

        # One of the previous reminders is pending to be sent
        if self.reminder_set.filter(reminder_sent__exact=False).count() > 0:
            return False

        return True

    def create_reminder(self):
        client = self.policy.client

        # Send reminder once every 30 days if past due
        if self.due_date < date.today() and self.premium_paid is False:
            due_date = None
            if self.reminder_set.exists() is True:
                last_reminder_date = self.reminder_set.latest('reminder_date').reminder_date
                days_after_last_reminder = abs(relativedelta(dt1=last_reminder_date, dt2=date.today()).days)
                if days_after_last_reminder >= 30:
                    due_date = date.today()
            else:
                due_date = date.today()

            if due_date is not None:
                Reminder.objects.create(due=self, reminder_date=due_date,
                                        mobile_number=client.mobile_number, email=client.email)

        # Create reminder if needed
        elif self.is_reminder_needed() is True:
            reminder_day = self.policy.premium_term.days_to_list()[self.reminder_set.count()]
            reminder_date = self.due_date + relativedelta(days=reminder_day)
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
