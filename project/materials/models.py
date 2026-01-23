from django.db import models
from construction.models import Project

class Material(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    stock = models.FloatField()
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name
    
class MaterialUsage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_used = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # only on first save
            self.material.stock -= self.quantity_used
            self.material.save()
        super().save(*args, **kwargs)

