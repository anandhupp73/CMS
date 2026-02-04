from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Labour, Attendance
from construction.models import *

def can_manage_labour(user):
    return user.role and user.role.name in ['Admin', 'Project Manager', 'Contractor']

def is_contractor(user):
    return user.is_authenticated and user.role and user.role.name == 'Contractor'

@login_required
@user_passes_test(can_manage_labour)
def labour_list(request):
    workers = Labour.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Only Admin and PM can add new workers to the master pool
        if request.user.role.name not in ['Admin', 'Project Manager']:
            messages.error(request, "Only Managers can register new workers.")
            return redirect('labour:labour_list')
            
        Labour.objects.create(
            name=request.POST.get('name'),
            wage_per_day=request.POST.get('wage_per_day')
        )
        messages.success(request, "Worker registered successfully.")
        return redirect('labour:labour_list')
        
    return render(request, 'labour/labour_list.html', {'workers': workers})

@login_required
@user_passes_test(can_manage_labour)
def project_attendance(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Fetch all phases for this project to populate the dropdown
    phases = project.phases.all() 
    workers = Labour.objects.all()
    
    # Updated to include phase in select_related for better performance
    attendance_history = Attendance.objects.filter(project=project).select_related('labour', 'phase').order_by('-date')

    if request.method == 'POST':
        labour_id = request.POST.get('labour_id')
        phase_id = request.POST.get('phase_id') # New field
        hours = int(request.POST.get('hours'))
        date = request.POST.get('date')
        
        worker = get_object_or_404(Labour, id=labour_id)
        phase = get_object_or_404(ProjectPhase, id=phase_id)

        Attendance.objects.create(
            project=project,
            phase=phase, # Logic now tracks exactly which phase the worker was on
            labour=worker,
            hours_worked=hours,
            date=date
        )
        messages.success(request, f"Attendance logged for {worker.name} on {phase.phase_name}")
        return redirect('labour:project_attendance', project_id=project.id)

    return render(request, 'labour/project_attendance.html', {
        'project': project,
        'phases': phases, # Pass phases to the template
        'workers': workers,
        'attendance_history': attendance_history
    })

@login_required
@user_passes_test(is_contractor)
def add_worker(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        wage = request.POST.get('wage_per_day')
        
        if name and wage:
            Labour.objects.create(name=name, wage_per_day=wage)
            messages.success(request, f"Worker {name} registered successfully.")
            return redirect('contractors:contractors_home')
            
    return render(request, 'labour/add_worker.html')

@login_required
@user_passes_test(can_manage_labour)
def view_project_workers(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Get unique workers who have attendance records for this project
    worker_ids = Attendance.objects.filter(project=project).values_list('labour', flat=True).distinct()
    active_workers = Labour.objects.filter(id__in=worker_ids)
    
    return render(request, 'labour/project_workers_list.html', {
        'project': project,
        'workers': active_workers
    })