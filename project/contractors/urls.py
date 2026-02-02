from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    path('', views.home, name='contractors_home'),
    path('invoice/submit/', views.submit_invoice, name='submit_invoice'),
    path('logs/', views.work_logs, name='work_logs'),
]