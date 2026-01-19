from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN','Admin'),
        ('PM','Project Manager'),
        ('SUP','Supervisor'),
        ('CONT','contractor'),
        ('ACC','Accountant'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)