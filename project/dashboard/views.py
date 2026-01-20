from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib import messages


@login_required
def dashboard_router(request):
    user = request.user
    role = user.role.name if user.role else None

    if role == 'Admin':
        return redirect('admin_dashboard')

    elif role == 'Project Manager':
        return redirect('construction_home')

    elif role == 'Supervisor':
        return redirect('labour_home')

    elif role == 'Contractor':
        return redirect('contractors_home')

    elif role == 'Accountant':
        return redirect('finance_home')

    messages.error(request, "No role assigned. Contact admin.")
    logout(request)
    return redirect('login')


def is_admin(user):
    return user.role and user.role.name == 'Admin'


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'dashboard/admin/dashboard.html')
