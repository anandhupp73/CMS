from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.contrib import messages
from .forms import AdminUserCreateForm
from construction.models import *
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from contractors.models import *
from materials.models import *
from finance.models import *
from decimal import Decimal

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



from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from materials.models import MaterialUsage
from finance.models import Payment

@login_required
@user_passes_test(is_admin)
def admin_view_projects(request):
    projects = Project.objects.prefetch_related('phases').order_by('-created_at')

    for project in projects:
        # 1. Physical Progress
        project.progress_percent = project.total_progress

        # 2. Actual Cash Paid (via Finance App)
        total_paid_cash = Payment.objects.filter(
            invoice__project=project
        ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')

        # 3. Material Value Consumed (via Materials App)
        total_material_cost = MaterialUsage.objects.filter(
            project=project
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity_used') * F('material__cost_per_unit'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total'] or Decimal('0.00')

        # 4. Final Financial Calculations
        project.spent_budget = total_paid_cash + total_material_cost
        
        # Initial Budget = Current Remaining + Spent
        initial_total = project.budget + project.spent_budget
        
        if initial_total > 0:
            project.budget_percent = round((project.spent_budget / initial_total) * 100, 2)
            project.initial_total = initial_total # To show the total on the card
        else:
            project.budget_percent = 0
            project.initial_total = 0

    return render(
        request,
        'dashboard/admin/admin_view_projects.html',
        {"projects": projects}
    )

@login_required
@user_passes_test(is_admin)
def admin_project_detail(request, project_id):
    project = get_object_or_404(Project.objects.prefetch_related(
        'phases', 'projectsupervisor_set__supervisor', 'projectcontractor_set__contractor'
    ), pk=project_id)

    # 1. Material Value (Consumed Resources)
    total_material_cost = MaterialUsage.objects.filter(project=project).aggregate(
        total=Sum(ExpressionWrapper(
            F('quantity_used') * F('material__cost_per_unit'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        ))
    )['total'] or Decimal('0.00')

    # 2. Total Paid Invoices (Actual Cash Outflow)
    # Using Payment model to get verified amounts paid by Accountant
    total_paid_cash = Payment.objects.filter(invoice__project=project).aggregate(
        total=Sum('paid_amount')
    )['total'] or Decimal('0.00')

    # 3. Total Spent Calculation
    spent_budget = total_material_cost + total_paid_cash

    # 4. Initial Budget (Since current budget is reducing, we calculate the start point)
    initial_budget = project.budget + spent_budget

    # 5. Budget Calculation for Progress Bar
    budget_percent = 0
    if initial_budget > 0:
        budget_percent = round((float(spent_budget) / float(initial_budget)) * 100, 2)

    context = {
        'project': project,
        'spent_budget': spent_budget,
        'budget_percent': budget_percent,
        'initial_budget': initial_budget, # Add this to context
        'total_material_cost': total_material_cost,
        'total_paid_cash': total_paid_cash,
        'invoices': Invoice.objects.filter(project=project).select_related('contractor', 'phase'),
        'material_usage': MaterialUsage.objects.filter(project=project).select_related('material', 'phase'),
    }
    return render(request, 'dashboard/admin/admin_proj_detail.html', context)