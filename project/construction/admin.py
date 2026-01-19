from django.contrib import admin
from .models import Project, ProjectPhase

class ProjectPhaseInline(admin.TabularInline):
    model = ProjectPhase
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'budget', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    inlines = [ProjectPhaseInline]

@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ('project', 'phase_name', 'progress', 'expected_end', 'actual_end')
