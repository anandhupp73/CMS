from django.contrib import admin
from .models import Contractor, Invoice

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'project', 'amount', 'status', 'created_at')
    list_filter = ('status',)
