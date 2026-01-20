from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_router, name='dashboard_router'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
