# python3 manage.py runcrons --force
# python3 manage.py runcrons "lic.cron.SampleCronJob"

import datetime
from django_cron import CronJobBase, Schedule
from lic.models import Policy, Due, Reminder
from lic.sendmail_html import send_reminder_mail

class SampleCronJob(CronJobBase):
    RUN_EVERY_MINS = 120 # every 2 hours

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
        self.create_reminders()
        reminders = []
        for reminder in Reminder.objects.all():
            if reminder.reminder_date <= datetime.date.today() and \
                reminder.due.premium_paid is False and \
                    reminder.reminder_sent is False:
                reminders.append(reminder)
        send_reminder_mail(reminders)
