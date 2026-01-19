from django.db import models
from django.conf import settings
from django.utils import timezone

#<<<<<<< HEAD
# =========================
# Batch Model
# =========================
class Batch(models.Model):
    name = models.CharField(max_length=100)
    
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='batches'
    )
    
    start_date = models.DateField()
    total_hours = models.PositiveIntegerField()
    total_students = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def student_count(self):
        return self.total_students
    
    @property
    def used_hours(self):
        return sum(s.hours_taken for s in self.sessions.all())
    
    @property
    def remaining_hours(self):
        return max(0, self.total_hours - self.used_hours)
    
    @property
    def delay_hours(self):
        return max(0, self.used_hours - self.total_hours)

# =========================
# Work Session Model
# =========================
class WorkSession(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

#=======

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
#>>>>>>> origin/main
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
#<<<<<<< HEAD

    session_date = models.DateField(default=timezone.now)
    hours_taken = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.batch.name} - {self.session_date}"
    # ✅ VALIDATION (warning logic)
    
# =========================
# Attendance Model
# =========================
class Attendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(null=True, blank=True)  # Added this field
    
    login_lat = models.FloatField(null=True, blank=True)
    login_lon = models.FloatField(null=True, blank=True)
    logout_lat = models.FloatField(null=True, blank=True)
    logout_lon = models.FloatField(null=True, blank=True)
    
    login_address = models.TextField(blank=True)
    logout_address = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total_time(self):
        if self.login_time and self.logout_time:
            return self.logout_time - self.login_time
        return None
    
    def save(self, *args, **kwargs):
        # Calculate total time before saving
        if self.login_time and self.logout_time:
            self.total_time = self.calculate_total_time()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time.date() if self.login_time else 'No login'}"

# =========================
# Trainer Attendance Model
# =========================
class TrainerAttendance(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date = models.DateField()
    mark_in_time = models.DateTimeField(null=True, blank=True)
    mark_out_time = models.DateTimeField(null=True, blank=True)
    working_duration = models.DurationField(null=True, blank=True)
    photo_in = models.ImageField(upload_to="attendance/in/", null=True, blank=True)
    photo_out = models.ImageField(upload_to="attendance/out/", null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['trainer', 'date']
        ordering = ['-date', '-mark_in_time']
    
    def __str__(self):
        return f"{self.trainer.username} - {self.date}"
#=======
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
#>>>>>>> origin/main
