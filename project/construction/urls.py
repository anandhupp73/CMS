from django.urls import path
from . import views

app_name = 'construction'

urlpatterns = [
    path('', views.home, name='construction_home'),
    path('add-project/', views.add_project, name='add_project'),
    path('project_manage/', views.project_manage, name='project_manage'),
    path('add-phase/<int:project_id>/',views.add_phase,name='add_phase'),
    path('add-supervisor/<int:project_id>',views.assign_supervisor,name='assign_supervisor'),
    path('update-progress/<int:project_id>',views.update_progress,name='update_progress'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('update-phase/<int:phase_id>/', views.update_phase, name='update_phase'),
    path('supervisors/', views.supervisors_list, name='pm_supervisors'),
    path('supervisor_dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('report-issue/<int:phase_id>/',views.report_issue,name='report_issue'),
    path('pm-issues/',views.pm_issues,name='pm_issues'),

    


]
