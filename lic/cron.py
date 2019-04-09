# python3 manage.py runcrons --force
# python3 manage.py runcrons "lic.cron.SampleCronJob"

import datetime
from django_cron import CronJobBase, Schedule
from lic.models import Policy, Due, Reminder
from lic.sendmail_html import send_reminder_mail
from dateutil.relativedelta import relativedelta

class SampleCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440 # every 24 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'lic.sampleCron'

    def create_dues(self):
        for policy in Policy.objects.all():
            policy.create_due()

    def create_reminders(self):
        for due in Due.objects.all():
            due.create_reminder()

    def do(self):
        self.create_dues()

        email_dues_list = []
        for due in Due.objects.filter(policy__policy_type__action_items__contains="Email",policy__due__premium_paid=False):
            yes = False
            r_set = due.reminder_set
            actions = due.policy.policy_type.actions()
            due_date = due.due_date

            # Is due date already past then send a reminder within a month

            if r_set.count() < len(actions.get('email_before', [])):
                yes = True

            if r_set.count() > 0:
                r = r_set.latest("-reminder_sent")
                days_after_last_reminder = abs(relativedelta(dt1=last_reminder_date, dt2=date.today()).days)

