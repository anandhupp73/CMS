from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('',RedirectView.as_view(url='/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  
    path('dashboard/', include('dashboard.urls')),
    path('construction/', include('construction.urls')),
    path('contractors/', include('contractors.urls')),
    path('materials/',include('materials.urls')),
    path('labour/',include('labour.urls')),
    path('finance/',include('finance.urls')),
]
