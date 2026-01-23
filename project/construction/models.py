from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Project(models.Model):
    name = models.CharField(max_length=200)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects'
    )

    manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='managed_projects',
        limit_choices_to={'role__name': 'Project Manager'}
    )

    start_date = models.DateField()
    end_date = models.DateField()

    budget = models.DecimalField(max_digits=15, decimal_places=2)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProjectPhase(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases'
    )

    phase_name = models.CharField(max_length=100)

    progress = models.PositiveIntegerField(default=0)

    expected_end = models.DateField()
    actual_end = models.DateField(null=True, blank=True)

    def is_delayed(self):
        return self.actual_end and self.actual_end > self.expected_end

    def __str__(self):
        return f"{self.project.name} - {self.phase_name}"

class ProjectSupervisor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__name': 'Supervisor'}
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'supervisor')
