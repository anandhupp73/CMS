from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_router, name='dashboard_router'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    path('admin/users/', views.user_list, name='admin_user_list'),
    path('admin/users/add/', views.user_create, name='admin_user_add'),
]
