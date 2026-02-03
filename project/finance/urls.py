from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.home, name='finance_home'),
    path('pay/<int:invoice_id>/', views.record_payment, name='record_payment'),
]
