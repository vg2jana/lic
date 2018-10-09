import os
from django_cron import CronJobBase, Schedule
from lic.models import Policy, Due, Reminder

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