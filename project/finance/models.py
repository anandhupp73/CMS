from django.db import models
from contractors.models import Invoice

class Payment(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_date = models.DateField(auto_now_add=True)
    mode = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment for Invoice {self.invoice.id}"