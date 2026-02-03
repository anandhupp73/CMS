from django.db import models
from construction.models import Project
from decimal import Decimal

class Labour(models.Model):
    name = models.CharField(max_length=100)
    wage_per_day = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    labour = models.ForeignKey(Labour, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.PositiveIntegerField()

    
    def calculate_wage(self):
        return (Decimal(self.hours_worked) / Decimal(8)) * self.labour.wage_per_day
    
