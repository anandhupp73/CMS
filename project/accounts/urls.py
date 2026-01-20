from django.urls import path
from . import views

urlpatterns = [
    path('', views.role_login, name='login'),
    path('logout/', views.logout_view, name="logout"),
]
