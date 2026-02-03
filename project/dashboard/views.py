from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.contrib import messages
from .forms import AdminUserCreateForm
from construction.models import *
from django.db.models import Sum
from decimal import Decimal
from contractors.models import *

User = get_user_model()

@login_required
def dashboard_router(request):
    user = request.user
    role = user.role.name if user.role else None

    if role == 'Admin':
        return redirect('admin_dashboard')

    elif role == 'Project Manager':
        return redirect('construction:construction_home')

    elif role == 'Supervisor':
        return redirect('construction:supervisor_dashboard')

    elif role == 'Contractor':
        return redirect('contractors:contractors_home')

    elif role == 'Accountant':
        return redirect('finance:finance_home')

    messages.error(request, "No role assigned. Contact admin.")
    logout(request)
    return redirect('login')


def is_admin(user):
    return user.role and user.role.name == 'Admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    print("User variable:", User)
    print("Type of User:", type(User))
    total_users = User.objects.count()
    pm_count = User.objects.filter(role__name='Project Manager').count()
    sup_count = User.objects.filter(role__name='Supervisor').count()
    print(total_users)
    
    active_projects = Project.objects.filter(is_active=True).order_by('-created_at')[:2]

    total_projects = Project.objects.count()
    active_count = Project.objects.filter(is_active=True).count()

    # Budgets
    total_budget = Project.objects.aggregate(
        total=Sum('budget')
    )['total'] or 0
    
    delayed_projects = 3
    overall_spending = 8_900_000  # $8.9M dummy
    spending_percentage = 71      # dummy %

    context = {
        'total_users': total_users,
        'pm_count': pm_count,
        'sup_count': sup_count,

        'total_projects': total_projects,
        'active_count': active_count,
        'delayed_projects': delayed_projects,

        'total_budget': total_budget,
        'overall_spending': overall_spending,
        'spending_percentage': spending_percentage,

        'active_projects': active_projects,
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
@user_passes_test(is_admin)
def admin_view_projects(request):
    projects = Project.objects.prefetch_related('phases')

    for project in projects:
        # Progress
        project.progress_percent = project.total_progress

        # ✅ Dummy spent budget (Decimal-safe)
        if project.budget:
            project.spent_budget = project.budget * Decimal('0.70')
            project.budget_percent = round(
                (project.spent_budget / project.budget) * Decimal('100'),
                2
            )
        else:
            project.spent_budget = Decimal('0')
            project.budget_percent = 0

    return render(
        request,
        'dashboard/admin/admin_view_projects.html',
        {"projects": projects}
    )


@login_required
@user_passes_test(is_admin)
def admin_project_detail(request, project_id):
    # Get project or 404
    project = get_object_or_404(Project, pk=project_id)

    # Calculate total spent budget from related invoices
    spent_budget = Invoice.objects.filter(
        project=project,
        status__in=['APPROVED', 'PAID']
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    # Calculate budget usage percent
    if project.budget:
        budget_percent = round(float(spent_budget) / float(project.budget) * 100, 2)
    else:
        budget_percent = 0

    context = {
        'project': project,
        'spent_budget': spent_budget,
        'budget_percent': budget_percent,
    }
    return render(request, 'dashboard/admin/admin_proj_detail.html', context)
