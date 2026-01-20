from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    path('', views.home, name='contractors_home'),
]
