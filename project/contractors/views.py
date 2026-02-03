from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from construction.models import *
from django.contrib import messages

def is_contractor(user):
    return  user.role and user.role.name == 'Contractor'

@login_required
@user_passes_test(is_contractor) 
def home(request):
    assignments = ProjectContractor.objects.filter(contractor=request.user).select_related('project')
    
    # Fetch invoices submitted by this user
    invoices = Invoice.objects.filter(contractor__contractor=request.user).order_by('-created_at')
    
    pending_count = invoices.filter(status='PENDING').count()
    context = {
        'assignments': assignments,
        'invoices': invoices,
        'pending_invoices': pending_count,
    }
    return render(request, 'contractors/contrac_dashboard.html', context)

@login_required
@user_passes_test(is_contractor)
def submit_invoice(request):
    # Fetch projects assigned to this contractor
    assignments = ProjectContractor.objects.filter(contractor=request.user)
    project_ids = assignments.values_list('project_id', flat=True)
    
    # Fetch all phases for those projects
    phases = ProjectPhase.objects.filter(project_id__in=project_ids).select_related('project')

    if request.method == 'POST':
        phase_id = request.POST.get('phase')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        selected_phase = get_object_or_404(ProjectPhase, id=phase_id)
        
        # Get the specific assignment record for the project this phase belongs to
        assignment = get_object_or_404(ProjectContractor, 
                                        contractor=request.user, 
                                        project=selected_phase.project)

        Invoice.objects.create(
            contractor=assignment,
            project=selected_phase.project,
            phase=selected_phase, # Link the invoice to the phase
            amount=amount,
            description=description,
            status='PENDING'
        )
        
        messages.success(request, f"Invoice for {selected_phase.phase_name} submitted successfully.")
        return redirect('contractors:contractors_home')

    return render(request, 'contractors/submit_invoice.html', {'phases': phases})