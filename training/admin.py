from django.contrib import admin
from .models import Batch, WorkSession

class WorkSessionInline(admin.TabularInline):
    model = WorkSession
    extra = 0
    readonly_fields = ('trainer', 'start_time', 'end_time', 'get_hours_spent', 'description')
    can_delete = False
    show_change_link = True

    # Display computed hours via a method
    @admin.display(description='Hours spent')
    def get_hours_spent(self, obj):
        return obj.hours_spent


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
        return obj.hours_spent
