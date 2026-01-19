from django.contrib import admin
from .models import Material, MaterialUsage

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'stock', 'cost_per_unit')
    search_fields = ('name',)

@admin.register(MaterialUsage)
class MaterialUsageAdmin(admin.ModelAdmin):
    list_display = ('project', 'material', 'quantity_used', 'date')
