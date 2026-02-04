from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import *
from django.shortcuts import get_object_or_404
from django.utils import timezone
from contractors.models import *

User = get_user_model()

def is_admin(user):
    return user.role and user.role.name == 'Admin'

def is_pm(user):
    return user.role and user.role.name == 'Project Manager'

def is_sup(user):
    return user.role and user.role.name == 'Supervisor'

def is_pm_or_sup(user):
    return user.role and user.role.name in ['Project Manager', 'Supervisor']



from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Subquery, OuterRef
from finance.models import Payment # Ensure these are imported
from materials.models import MaterialUsage

@login_required
@user_passes_test(is_pm)
def home(request):
    
    projects = Project.objects.filter(manager=request.user).annotate(
        total_spent=Subquery(
            Payment.objects.filter(invoice__project=OuterRef('pk'))
            .values('invoice__project')
            .annotate(sum=Sum('paid_amount'))
            .values('sum')
        )
    ).prefetch_related('phases')

    return render(request, 'construction/pm_dashboard.html', {'projects': projects})

@login_required
@user_passes_test(is_admin)
def add_project(request):
    project_managers = User.objects.filter(role__name='Project Manager')

    if request.method == 'POST':
        name = request.POST.get('name')
        manager_id = request.POST.get('manager')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget')
        is_active = request.POST.get('is_active') == 'on'


        if not all([name, manager_id, start_date, end_date, budget]):
            messages.error(request, "All fields are required")
            return redirect('construction:add_project')
        
        manager = User.objects.get(id=manager_id)

        Project.objects.create(
            name = name,
            created_by = request.user,
            manager = manager,
            start_date = start_date,
            end_date = end_date,
            budget = budget,
            is_active = is_active,
        )

        messages.success(request, "Project created succesfully")
        return redirect('admin_dashboard')
    
    return render(request, 'construction/add_project.html',{ 'project_managers' : project_managers })

@login_required
@user_passes_test(is_pm)
def project_manage(request):
    return render(request, 'construction/project_manage.html')

@login_required
@user_passes_test(is_pm)
def add_phase(request, project_id):
    project = Project.objects.get(id=project_id)

    if request.method == 'POST':
        phase_name = request.POST.get('phase_name')
        expected_end = request.POST.get('expected_end')

        if not phase_name or not expected_end:
            messages.error(request, "All fields are required.")
            return redirect('add_phase', project_id=project.id)

        ProjectPhase.objects.create(
            project=project,
            phase_name=phase_name,
            expected_end=expected_end
        )

        messages.success(request, "Phase added successfully.")
        return redirect('construction:construction_home')

    return render(request, 'construction/add_phase.html', {
        'project': project
    })

@login_required
@user_passes_test(is_pm)
def assign_supervisor(request, project_id):
    project = Project.objects.get(id=project_id)

    supervisors = User.objects.filter(role__name='Supervisor', is_active=True)

    if request.method == 'POST':
        supervisor_id = request.POST.get('supervisor')
        supervisor = User.objects.get(id=supervisor_id)

        ProjectSupervisor.objects.create(
            project=project,
            supervisor=supervisor
        )

        messages.success(request, "Supervisor assigned")
        return redirect('construction:construction_home')

    return render(request, 'construction/assign_supervisor.html', {
        'project': project,
        'supervisors': supervisors
    })

@login_required
@user_passes_test(is_pm)
def update_progress(request, project_id):
    project = Project.objects.get(id=project_id)

    phases = project.phases.all()

    if request.method == 'POST':
        for phase in phases:
            progress = request.POST.get(f'phase_{phase.id}')
            if progress:
                phase.progress = int(progress)
                phase.save()

        messages.success(request, "Progress updated")
        return redirect('construction:construction_home')

    return render(request, 'construction/update_progress.html', {
        'project': project,
        'phases': phases
    })

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    phases = project.phases.all()
    supervisors = ProjectSupervisor.objects.filter(project=project).select_related('supervisor')
    
    # NEW: Fetch Contractors
    contractors = ProjectContractor.objects.filter(project=project).select_related('contractor')
    
    # NEW: Financial Calculations for the Header Cards
    # 1. Total Cash Actually Paid
    total_paid_cash = Payment.objects.filter(
        invoice__project=project
    ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')

    # 2. Total Material Value Consumed
    total_material_cost = MaterialUsage.objects.filter(
        project=project
    ).aggregate(
        total=Sum(ExpressionWrapper(
            F('quantity_used') * F('material__cost_per_unit'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        ))
    )['total'] or Decimal('0.00')

    # 3. Reconstruct the Initial Budget (Since we subtract from 'budget' field directly)
    original_total = project.budget + total_paid_cash + total_material_cost

    return render(request, 'construction/project_detail.html', {
        'project': project,
        'phases': phases,
        'supervisors': supervisors,
        'contractors': contractors,
        'total_paid_cash': total_paid_cash,
        'total_material_cost': total_material_cost,
        'original_total': original_total,
    })

@login_required
@user_passes_test(is_pm)
def pm_issues(request):
    # All reported issues for projects managed by this PM
    issues = Issue.objects.filter(
        project__manager=request.user
    ).select_related('phase', 'project', 'reported_by')
    
    delayed_phases = ProjectPhase.objects.filter(
        project__manager=request.user,
        expected_end__lt=timezone.now(),
        actual_end__isnull=True
    ).select_related('project')

    return render(request, 'construction/pm_issues.html', {
        'issues': issues,
        'delayed_phases': delayed_phases
    })


@login_required
@user_passes_test(is_pm_or_sup)
def update_phase(request, phase_id):
    user = request.user

    # PM: can update phases of projects they manage
    if user.role.name == 'Project Manager':
        phase = get_object_or_404(
            ProjectPhase,
            id=phase_id,
            project__manager=user
        )

    # Supervisor: can update phases of projects they are assigned to
    else:
        phase = get_object_or_404(
            ProjectPhase,
            id=phase_id,
            project__projectsupervisor__supervisor=user
        )

    if request.method == 'POST':
        phase.progress = request.POST.get('progress')

        actual_end = request.POST.get('actual_end')
        phase.actual_end = actual_end if actual_end else None

        phase.save()

        # Redirect based on role
        if user.role.name == 'Supervisor':
            return redirect('construction:supervisor_dashboard')

        return redirect('construction:project_detail', phase.project.id)

    return render(request, 'construction/update_phase.html', {
        'phase': phase
    })


@login_required
def supervisors_list(request):
    supervisors = ProjectSupervisor.objects.filter(
        project__manager=request.user
    ).select_related('supervisor', 'project')

    return render(request, 'construction/supervisor_list.html', {
        'supervisors': supervisors
    })

@login_required
@user_passes_test(is_sup)
def supervisor_dashboard(request):
    assigned_projects = Project.objects.filter(projectsupervisor__supervisor=request.user)
    
    assigned_phases = ProjectPhase.objects.filter(project__in=assigned_projects).select_related('project')

    recent_logs = DailySiteLog.objects.filter(supervisor=request.user).order_by('-date')[:5]

    return render(request, 'construction/supervisor_dashboard.html', {
        'assigned_projects': assigned_projects,
        'assigned_phases': assigned_phases,
        'recent_logs': recent_logs
    })

@login_required
@user_passes_test(is_sup)
def submit_daily_log(request):
    # CRITICAL: We must fetch these so the sidebar/navbar links don't crash
    assigned_projects = Project.objects.filter(projectsupervisor__supervisor=request.user)
    
    # This is what line 118 in your dashboard template is looking for!
    assigned_phases = ProjectPhase.objects.filter(project__in=assigned_projects).select_related('project')

    if request.method == 'POST':
        project_id = request.POST.get('project')
        work_done = request.POST.get('work_done')
        weather = request.POST.get('weather_condition')
        photo = request.FILES.get('photo')

        DailySiteLog.objects.create(
            project_id=project_id,
            supervisor=request.user,
            work_done=work_done,
            weather_condition=weather,
            photo=photo
        )
        messages.success(request, "Daily Journal updated successfully.")
        return redirect('construction:supervisor_dashboard')

    return render(request, 'construction/submit_daily_log.html', {
        'projects': assigned_projects,      
        'assigned_projects': assigned_projects, 
        'assigned_phases': assigned_phases      
    })
    
@login_required
@user_passes_test(is_sup)
def report_issue(request, phase_id):
    phase = ProjectPhase.objects.get(
        id=phase_id,
        project__projectsupervisor__supervisor=request.user
    )

    if request.method == 'POST':
        Issue.objects.create(
            project=phase.project,
            phase=phase,
            reported_by=request.user,
            issue_type=request.POST['issue_type'],
            description=request.POST['description']
        )
        messages.success(request, "Issue reported successfully")
        return redirect('construction:supervisor_dashboard')

    return render(request, 'construction/report_issue.html', {
        'phase': phase
    })

@login_required
@user_passes_test(is_pm)
def assign_contractor(request, project_id):
    project = Project.objects.get(id=project_id)

    contractors = User.objects.filter(role__name='Contractor', is_active=True)

    if request.method == 'POST':
        contractor_id = request.POST.get('contractor')
        contractor = User.objects.get(id=contractor_id)

        ProjectContractor.objects.create(
            project=project,
            contractor=contractor
        )

        messages.success(request, "contractor assigned")
        return redirect('construction:construction_home')


    return render(request, 'construction/assign_contractor.html',{
        'project':project,
        'contractors':contractors
    })
    
