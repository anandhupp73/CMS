from django.urls import path
from . import views

app_name = 'labour'

urlpatterns = [
    path('', views.home, name='labour_home'),
]
