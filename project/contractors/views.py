from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from construction.models import *
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum, ExpressionWrapper, F, DecimalField
from django.db import transaction

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
    phases = ProjectPhase.objects.filter(project_id__in=project_ids).select_related('project')

    if request.method == 'POST':
        phase_id = request.POST.get('phase')
        # Contractor's manual entry for extra work/labour
        try:
            extra_costs = Decimal(request.POST.get('extra_costs') or '0')
        except:
            extra_costs = Decimal('0.00')
            
        description = request.POST.get('description', '')
        selected_phase = get_object_or_404(ProjectPhase, id=phase_id)

        # Wrap in transaction to ensure data integrity
        with transaction.atomic():
            # 1. CALCULATE MATERIALS (Float * Decimal Fix)
            # We use the related_name='material_logs' from your model
            mat_value = selected_phase.material_logs.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F('quantity_used') * F('material__cost_per_unit'),
                        output_field=DecimalField(max_digits=15, decimal_places=2)
                    )
                )
            )['total'] or Decimal('0.00')

            # 2. CALCULATE LABOUR ATTENDANCE
            # Since 'daily_wage' is a @property, we calculate in Python
            # Use related_name='attendance_logs' from your model
            labour_logs = selected_phase.attendance_logs.all()
            labour_value = sum((log.daily_wage for log in labour_logs), Decimal('0.00'))

            # 3. CALCULATE GRAND TOTAL
            grand_total = mat_value + labour_value + extra_costs

            # 4. GET CONTRACTOR ASSIGNMENT
            assignment = get_object_or_404(
                ProjectContractor, 
                contractor=request.user, 
                project=selected_phase.project
            )

            # 5. CREATE THE INVOICE
            # We store the breakdown in the description so the Accountant can see it
            detailed_desc = (
                f"--- AUTO-CALCULATED BREAKDOWN ---\n"
                f"Materials: ${mat_value:,.2f}\n"
                f"Labour Attendance: ${labour_value:,.2f}\n"
                f"Contractor Service Fee: ${extra_costs:,.2f}\n"
                f"----------------------------------\n"
                f"Notes: {description}"
            )

            Invoice.objects.create(
                contractor=assignment,
                project=selected_phase.project,
                phase=selected_phase,
                amount=grand_total,
                description=detailed_desc,
                status='PENDING'
            )

        messages.success(request, f"Invoice for {selected_phase.phase_name} (${grand_total:,.2f}) submitted successfully.")
        return redirect('contractors:contractors_home')

    return render(request, 'contractors/submit_invoice.html', {'phases': phases})