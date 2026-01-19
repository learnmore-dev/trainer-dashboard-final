from django.db import models
from django.conf import settings
from django.utils import timezone

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

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

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