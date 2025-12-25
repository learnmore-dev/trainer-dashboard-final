from django.db import models
from django.conf import settings
from django.utils import timezone


class Attendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        null=True,
        blank=True
    )
    
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    login_lat = models.FloatField(null=True, blank=True)
    login_lon = models.FloatField(null=True, blank=True)
    login_address = models.TextField(null=True, blank=True)

    logout_lat = models.FloatField(null=True, blank=True)
    logout_lon = models.FloatField(null=True, blank=True)
    logout_address = models.TextField(null=True, blank=True)

    total_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.login_time.date() if self.login_time else 'No login'}"
        return f"Attendance {self.id}"


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
        start_date = self.start_datetime.date()
        end_date = self.end_datetime.date()
        
        if now < start_date:
            return 0
        if now > end_date:
            return self.total_days
        return (now - start_date).days + 1

    @property
    def days_remaining(self):
        now = timezone.now().date()
        end_date = self.end_datetime.date()
        
        if now >= end_date:
            return 0
        return (end_date - now).days + 1


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
            return 0
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 3600, 2)