from django.urls import path
from . import views

urlpatterns = [
    path('', views.role_login, name='role_login'),
    path('logout/', views.custom_logout, name="logout"),
    
]
