from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.material_bank, name='material_home'),
    path('project/<int:project_id>/usage/', views.project_material_usage, name='project_usage'),
]
