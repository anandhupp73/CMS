from django.urls import path
from . import views

app_name = 'labour'

urlpatterns = [
    path('', views.labour_list, name='labour_home'),
    path('add-worker/', views.add_worker, name='add_worker'),
    path('project/<int:project_id>/attendance/', views.project_attendance, name='project_attendance'),
    path('view-workers/<int:project_id>/', views.view_project_workers, name='view_project_workers'),
]
