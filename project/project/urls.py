from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('accounts.urls')),  
    path('logout/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('construction/', include('construction.urls')),
]
