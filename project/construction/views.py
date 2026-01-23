from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import *

User = get_user_model()

def is_admin(user):
    return user.role and user.role.name == 'Admin'

@login_required
def home(request):

    projets = Project.objects.filter(manager=request.user)
    return render(request, 'construction/pm_dashboard.html',{ 'projects': projets})

def add_project(request):
    project_managers = User.objects.filter(role__name='Project Manager')

    if request.method == 'POST':
        name = request.POST.get('name')
        manager_id = request.POST.get('manager')
        start_date = request.POST.get('start_date')
        end_date = request.POST('end_date')
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