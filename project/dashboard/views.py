from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    role = request.user.role
    if role == 'ADMIN':
        return render(request, 'dashboard/admin.html')
    elif role == 'PM':
        return render(request, 'dashboard/pm.html')
    elif role == 'SUP':
        return render(request, 'dashboard/supervisor.html')
    elif role == 'CONT':
        return render(request, 'dashboard/contractor.html')
    elif role == 'ACC':
        return render(request, 'dashboard/accountant.html')
