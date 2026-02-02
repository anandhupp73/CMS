from django.contrib import admin
from .models import ProjectContractor, Invoice

@admin.register(ProjectContractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'project', 'get_email', 'assigned_at') 

    def get_email(self, obj):
        return obj.contractor.email
    get_email.short_description = 'Contractor Email'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'project', 'amount', 'status', 'created_at')
    list_filter = ('status',)