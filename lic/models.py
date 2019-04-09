from django.db import models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import ast

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


class PolicyType(models.Model):
    policy_name = models.CharField(max_length=200)
    policy_type_choices = (
        ("E", "Email"),
        ("P", "PDF Generation")
    )
    action_items = models.CharField(max_length=100, blank=True, verbose_name="Select actions that apply to this policy type")
    type_choices = (
        ("H", "Health Insurance"),
        ("G", "General Insurance")
    )
    policy_type = models.CharField(max_length=1, choices=type_choices, default="H")

    def __str__(self):
        return str(self.policy_name)

    def email_args(self):
        return {
            "email_before": (-15, -2),
        }

    def actions(self):
        action_items = ast.literal_eval(self.action_items)
        actions = {}
        if 'E' in action_items:
            email_args = self.email_args()
            if email_args is not None:
                actions.update(email_args)
        return actions

    def actions_choices_text(self):
        text_list = [str(x) for x in self.action_items.split(',')]
        return ','.join(text_list)


class Policy(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    policy_type = models.ForeignKey(PolicyType, on_delete=models.CASCADE)
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
    added_date = models.DateField(default=datetime.now)

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
        premium_paid = False
        if due_date < self.added_date:
            premium_paid = True
        Due.objects.create(policy=self, due_date=due_date, premium_paid=premium_paid)
        self.create_due()

    def is_paid(self):
        return self.latest_due().paid

class Due(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    premium_paid = models.BooleanField(default=False)
    due_date = models.DateField()

    def __str__(self):
        return "Policy({}) Due_date: {}".format(self.policy.number, self.due_date)

    def paid(self):
        if self.premium_paid is True:
            return "Paid"
        else:
            return "Not Paid"

    def grace_date(self):
        return self.due_date + relativedelta(months=1)

    def email_before(self):
        return self.policy.policy_type.actions().get('email_before')

    def is_reminder_needed(self):
        if self.premium_paid is True:
            return False

        if self.reminder_set.exists() is False:
            return True

        if self.reminder_set.count() >= len(self.email_before()):
            return False

        if self.reminder_set.filter(reminder_sent__exact=False).count() > 0:
            return False

        return True

    def create_reminder(self):
        client = self.policy.client
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
        elif self.is_reminder_needed() is True:
            reminder_day = self.email_before()[self.reminder_set.count()]
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
