from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('role_login')

urlpatterns = [
    path('', home_redirect, name='home'),         
    path('login/', include('accounts.urls')),     
    path('dashboard/', include('dashboard.urls')), 
    path('admin/', admin.site.urls),
]
