<<<<<<< HEAD
from django.contrib import admin
from django.utils.html import format_html
from .models import Batch, WorkSession, Attendance, TrainerAttendance

# ================== WorkSession Inline ==================
class WorkSessionInline(admin.TabularInline):
    model = WorkSession
    extra = 0
    can_delete = False
    show_change_link = True
    
    readonly_fields = (
        'trainer',
        'session_date',
        'hours_taken',
        'description',
    )

# ================== Batch Admin ==================
@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'trainer',
        'start_date',
        'total_hours',
        'student_count',
        'used_hours_display',
        'remaining_hours_display',
        'delay_hours_display',
        'status_badge',
    )
    
    list_filter = ('trainer', 'start_date')
    ordering = ('start_date',)
    search_fields = ('name', 'trainer__username')
    inlines = [WorkSessionInline]
    
    @admin.display(description="Used Hours")
    def used_hours_display(self, obj):
        return obj.used_hours
    
    @admin.display(description="Remaining Hours")
    def remaining_hours_display(self, obj):
        return max(0, obj.remaining_hours)
    
    @admin.display(description="Delay Hours")
    def delay_hours_display(self, obj):
        return obj.delay_hours
    
    # ✅ COLOR BADGE
    @admin.display(description="Status")
    def status_badge(self, obj):
        if obj.delay_hours > 0:
            return format_html('<span style="color: red; font-weight: bold;">🔴 DELAY</span>')
        return format_html('<span style="color: green; font-weight: bold;">🟢 ON TRACK</span>')

# ================== WorkSession Admin ==================
@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = (
        'trainer',
        'batch',
        'session_date',
        'hours_taken',
        'description',
    )
    
    list_filter = ('batch', 'trainer', 'session_date')
    search_fields = ('trainer__username', 'batch__name', 'description')
    ordering = ('-session_date',)

# ================== Attendance Admin ==================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'login_time',
        'logout_time',
        'login_address',
        'total_time_display',
    )
    
    list_filter = ('login_time', 'user')
    search_fields = ('user__username', 'login_address', 'logout_address')
    readonly_fields = ('total_time',)
=======
# admin.py

from django.contrib import admin
from .models import Batch, WorkSession, Attendance

class WorkSessionInline(admin.TabularInline):
    model = WorkSession
    extra = 0
    readonly_fields = ('trainer', 'start_time', 'end_time', 'get_hours_spent', 'description')
    can_delete = False
    show_change_link = True

    @admin.display(description='Hours spent')
    def get_hours_spent(self, obj):
        return f"{obj.hours_spent:.2f}"

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'start_datetime', 'end_datetime', 'total_days', 'days_remaining')
    list_filter = ('trainer', 'start_datetime', 'end_datetime')
    search_fields = ('name', 'trainer__username')
    inlines = [WorkSessionInline]
    ordering = ('start_datetime',)

@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'batch', 'start_time', 'end_time', 'get_hours_spent', 'description')
    list_filter = ('batch', 'trainer', 'start_time')
    search_fields = ('trainer__username', 'batch__name', 'description')
    ordering = ('-start_time',)
    readonly_fields = ('get_hours_spent',)

    @admin.display(description='Hours spent')
    def get_hours_spent(self, obj):
        return f"{obj.hours_spent:.2f}"

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'login_address', 'total_time_display')
    list_filter = ('login_time', 'user')
    search_fields = ('user__username', 'login_address', 'logout_address')
>>>>>>> origin/main
    
    @admin.display(description='Total Time')
    def total_time_display(self, obj):
        if obj.total_time:
<<<<<<< HEAD
            seconds = obj.total_time.total_seconds()
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "N/A"

# ================== Trainer Attendance Admin ==================
@admin.register(TrainerAttendance)
class TrainerAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "trainer",
        "date",
        "mark_in_time",
        "mark_out_time",
        "working_duration_display",
        "photo_in_preview",
        "photo_out_preview",
    )
    
    readonly_fields = (
        "photo_in_preview",
        "photo_out_preview",
        "working_duration_display",
    )
    
    list_filter = ("date", "trainer")
    search_fields = ("trainer__username", "date")
    ordering = ("-date", "-mark_in_time")
    
    # ---------- PHOTO IN PREVIEW ----------
    def photo_in_preview(self, obj):
        if obj.photo_in:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:8px;" />',
                obj.photo_in.url
            )
        return "No Photo"
    
    photo_in_preview.short_description = "Photo In"
    
    # ---------- PHOTO OUT PREVIEW ----------
    def photo_out_preview(self, obj):
        if obj.photo_out:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:8px;" />',
                obj.photo_out.url
            )
        return "No Photo"
    
    photo_out_preview.short_description = "Photo Out"
    
    # ---------- WORKING DURATION DISPLAY ----------
    @admin.display(description="Working Duration")
    def working_duration_display(self, obj):
        if obj.working_duration:
            total_seconds = int(obj.working_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "--"
=======
            hours = int(obj.total_time.total_seconds() // 3600)
            minutes = int((obj.total_time.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "N/A"
>>>>>>> origin/main
