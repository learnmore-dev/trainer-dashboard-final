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
    
    @admin.display(description='Total Time')
    def total_time_display(self, obj):
        if obj.total_time:
            hours = int(obj.total_time.total_seconds() // 3600)
            minutes = int((obj.total_time.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "N/A"