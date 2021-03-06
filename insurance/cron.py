# python3 manage.py runcrons --force
# python3 manage.py runcrons "insurance.cron.SampleCronJob"

import datetime
from django_cron import CronJobBase, Schedule
from insurance.models import Policy, Due, Reminder
from insurance.sendmail_html import send_reminder_mail

class SampleCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440 # every 24 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'insurance.sampleCron'

    def create_dues(self):
        for policy in Policy.objects.all():
            policy.create_due()

    def create_reminders(self):
        for due in Due.objects.all():
            due.create_reminder()

    def do(self):
        self.create_dues()
        self.create_reminders()
        reminders = []
        for reminder in Reminder.objects.all():
            if reminder.reminder_date <= datetime.date.today() and \
                reminder.due.premium_paid is False and \
                    reminder.reminder_sent is False:
                reminders.append(reminder)
        send_reminder_mail(reminders)
