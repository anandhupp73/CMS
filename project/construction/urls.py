from django.urls import path
from . import views

app_name = 'construction'

urlpatterns = [
    path('', views.home, name='construction_home'),
    path('add-project/', views.add_project, name='add_project'),
    path('project_manage/', views.project_manage, name='project_manage'),
]
