from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.material_bank, name='material_home'),
    path('project/<int:project_id>/usage/', views.project_material_usage, name='project_usage'),
    path('update-stock/<int:material_id>/', views.update_material_stock, name='update_stock'),
]
