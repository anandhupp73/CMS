from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_router, name='dashboard_router'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    path('admin/users/', views.user_list, name='admin_user_list'),
    path('admin/users/add/', views.user_create, name='admin_user_add'),
    path('admin-view-project/', views.admin_view_projects, name="admin_view_projects"),
    path('admin-project-detail/<int:project_id>/',views.admin_project_detail,name="admin_project_detail"),
    path('issue/<int:issue_id>/', views.admin_issue_detail, name='admin_issue_detail'),
    path('invoice/<int:invoice_id>/', views.admin_invoice_detail, name='admin_invoice_detail'),
]
