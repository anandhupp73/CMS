from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Material, MaterialUsage
from construction.models import Project


def can_manage_materials(user):
    return user.role and user.role.name in ['Admin', 'Project Manager', 'Contractor']

def can_add_materials(user):
    return user.role and user.role.name in ['Admin', 'Project Manager']
    

@login_required
@user_passes_test(can_manage_materials)
def material_bank(request):
    materials = Material.objects.all().order_by('name')
    
    if request.method == 'POST':
        
        if request.user.role.name not in ['Admin', 'Project Manager']:
            messages.error(request, "Only Managers can add new material types.")
            return redirect('materials:material_bank')
        
        initial_stock = float(request.POST.get('initial_stock'))
            
        Material.objects.create(
            name=request.POST.get('name'),
            unit=request.POST.get('unit'),
            initial_stock=initial_stock,
            stock=initial_stock,
            cost_per_unit=request.POST.get('cost_per_unit')
        )
        messages.success(request, "Material added to master bank.")
        return redirect('materials:material_home')
        
    return render(request, 'materials/material_list.html', {'materials': materials})

@login_required
@user_passes_test(can_manage_materials)
def project_material_usage(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    materials = Material.objects.all()
    usage_history = MaterialUsage.objects.filter(project=project).select_related('material').order_by('-date')

    if request.method == 'POST':
        mat_id = request.POST.get('material_id')
        qty = float(request.POST.get('quantity'))
        material = get_object_or_404(Material, id=mat_id)

        if material.stock >= qty:
            # MaterialUsage.save() automatically handles stock deduction
            MaterialUsage.objects.create(project=project, material=material, quantity_used=qty)
            messages.success(request, f"Logged {qty} {material.unit} of {material.name}")
        else:
            messages.error(request, f"Insufficient stock for {material.name}!")
        
        return redirect('materials:project_usage', project_id=project.id)

    return render(request, 'materials/project_usage.html', {
        'project': project,
        'materials': materials,
        'usage_history': usage_history
    })