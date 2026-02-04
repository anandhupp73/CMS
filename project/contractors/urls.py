from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    path('', views.home, name='contractors_home'),
    path('invoice/submit/', views.submit_invoice, name='submit_invoice'),
    path('api/get-phase-costs/', views.get_phase_costs, name='get_phase_costs'),
]