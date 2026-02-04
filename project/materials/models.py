from django.db import models
from construction.models import *
from django.db.models import Sum

class Material(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    initial_stock = models.FloatField(default=0)  # Starting stock
    stock = models.FloatField(default=0)          # Current stock
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name
    
    @property
    def total_used(self):
        # This looks at the related MaterialUsage records and sums 'quantity_used'
        usage = self.materialusage_set.aggregate(total=Sum('quantity_used'))['total']
        return usage if usage else 0.0
    
class MaterialUsage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # NEW: Link usage to a specific phase
    phase = models.ForeignKey(
        ProjectPhase, 
        on_delete=models.CASCADE, 
        related_name='material_logs',
        null=True, # Allows existing logs to remain valid
        blank=True
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_used = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # When saving, deduct from the main Material bank
            self.material.stock -= self.quantity_used
            self.material.save()
        super().save(*args, **kwargs)

