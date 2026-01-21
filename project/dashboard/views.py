from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib import messages
from accounts.models import *
from .forms import AdminUserCreateForm


@login_required
def dashboard_router(request):
    user = request.user
    role = user.role.name if user.role else None

    if role == 'Admin':
        return redirect('admin_dashboard')

    elif role == 'Project Manager':
        return redirect('construction:construction_home')

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
    total_users = User.objects.count()
    pm_count = User.objects.filter(role__name='Project Manager').count()
    sup_count = User.objects.filter(role__name='Supervisor').count()

    context = {
        'total_users': total_users,
        'pm_count': pm_count,
        'sup_count': sup_count,
    }
    return render(request, 'dashboard/admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'dashboard/admin/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            return redirect('admin_user_list')
    else:
        form = AdminUserCreateForm()

    return render(request, 'dashboard/admin/user_form.html', {
        'form': form,
        'title': 'Add User'
    })

@login_required
def constrction_home(request):
    return render(request, 'dashboard/pm/pm_dashboard.html')
