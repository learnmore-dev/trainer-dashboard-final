from django.db import models
from django.conf import settings
from django.utils import timezone

class Batch(models.Model):
    name = models.CharField(max_length=255)
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batches'
    )
    start_datetime = models.DateTimeField()
    end_datetime   = models.DateTimeField()
    notes          = models.TextField(blank=True, null=True)

    def __str__(self):
        trainer_name = self.trainer.username if self.trainer else "Unassigned"
        return f"{self.name} (Trainer: {trainer_name})"

    @property
    def total_days(self):
        return (self.end_datetime.date() - self.start_datetime.date()).days + 1

    @property
    def days_elapsed(self):
        now = timezone.now().date()
        if now < self.start_datetime.date():
            return 0
        if now > self.end_datetime.date():
            return self.total_days
        return (now - self.start_datetime.date()).days + 1

    @property
    def days_remaining(self):
        now = timezone.now().date()
        if now >= self.end_datetime.date():
            return 0
        return (self.end_datetime.date() - now).days + 1


class WorkSession(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='work_sessions'
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    start_time = models.DateTimeField(blank=True, null=True)
    end_time   = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.start_time:
            ts = self.start_time.strftime('%Y-%m-%d %H:%M')
        else:
            ts = 'N/A'
        return f"{self.trainer.username} — {self.batch.name} @ {ts}"

    @property
    def hours_spent(self):
        if not self.start_time or not self.end_time:
            return None
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600
