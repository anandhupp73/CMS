from django.db import models
from django.conf import settings
from construction.models import Project

User = settings.AUTH_USER_MODEL

class ProjectContractor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contractor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role__name': 'Contractor'}
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'contractor')



class Invoice(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
    )

    contractor = models.ForeignKey(ProjectContractor, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # NEW FIELD: Direct link to the phase
    phase = models.ForeignKey('construction.ProjectPhase', on_delete=models.CASCADE, related_name='invoices',null=True,blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Inv #{self.id} - {self.phase.phase_name} ({self.project.name})"