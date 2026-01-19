from django.contrib import admin
from .models import Labour, Attendance

@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = ('name', 'wage_per_day')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('labour', 'project', 'date', 'hours_worked')
