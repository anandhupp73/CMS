from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Material, MaterialUsage
from construction.models import *
from django.db.models import Sum
from django.db.models.functions import Coalesce


def can_manage_materials(user):
    return user.role and user.role.name in ['Admin', 'Project Manager', 'Contractor']

def can_add_materials(user):
    return user.role and user.role.name in ['Admin', 'Project Manager']
    

@login_required
@user_passes_test(can_manage_materials)
def material_bank(request):
    materials = Material.objects.annotate(
        total_used_calc=Coalesce(Sum('materialusage__quantity_used'), 0.0)
    ).order_by('name')
    
    if request.method == 'POST':
        
        if request.user.role.name not in ['Admin', 'Project Manager']:
            messages.error(request, "Only Managers can add new material types.")
            return redirect('materials:material_bank')
        
        initial_stock = float(request.POST.get('initial_stock'))
        cost_per_unit = float(request.POST.get('cost_per_unit'))

            
        Material.objects.create(
            name=request.POST.get('name'),
            unit=request.POST.get('unit'),
            initial_stock=initial_stock,
            stock=initial_stock,
            cost_per_unit=cost_per_unit
        )
        messages.success(request, "Material added to master bank.")
        return redirect('materials:material_home')
        
    return render(request, 'materials/material_list.html', {'materials': materials})

@login_required
@user_passes_test(can_manage_materials)
def project_material_usage(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Fetch all phases for this project to populate the dropdown
    phases = project.phases.all() 
    materials = Material.objects.all()
    # Updated to include phase in the select_related for better performance
    usage_history = MaterialUsage.objects.filter(project=project).select_related('material', 'phase').order_by('-date')

    if request.method == 'POST':
        mat_id = request.POST.get('material_id')
        phase_id = request.POST.get('phase_id') # Capture the selected phase
        qty = float(request.POST.get('quantity'))
        
        material = get_object_or_404(Material, id=mat_id)
        phase = get_object_or_404(ProjectPhase, id=phase_id)

        if material.stock >= qty:
            # Create usage record linked to the specific phase
            MaterialUsage.objects.create(
                project=project, 
                phase=phase, # Logic now tracks exactly which phase used the stock
                material=material, 
                quantity_used=qty
            )
            messages.success(request, f"Logged {qty} {material.unit} of {material.name} for {phase.phase_name}")
        else:
            messages.error(request, f"Insufficient stock for {material.name}!")
        
        return redirect('materials:project_usage', project_id=project.id)

    return render(request, 'materials/project_usage.html', {
        'project': project,
        'phases': phases, 
        'materials': materials,
        'usage_history': usage_history
    })
    
@login_required
@user_passes_test(can_add_materials)
def update_material_stock(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        added_qty = float(request.POST.get('added_quantity'))
        material.stock += added_qty 
        material.save()
        messages.success(request, f"Added {added_qty} to stock.")
        return redirect('materials:material_home')
    return render(request, 'materials/update_stock.html', {'material': material})