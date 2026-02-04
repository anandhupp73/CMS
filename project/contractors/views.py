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
    assignments = ProjectContractor.objects.filter(contractor=request.user)
    project_ids = assignments.values_list('project_id', flat=True)
    phases = ProjectPhase.objects.filter(project_id__in=project_ids).select_related('project')

    if request.method == 'POST':
        phase_id = request.POST.get('phase')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        extra_costs = Decimal(request.POST.get('extra_costs') or '0')
        description = request.POST.get('description', '')

        selected_phase = get_object_or_404(ProjectPhase, id=phase_id)

        with transaction.atomic():
            # 1. FILTER MATERIALS BY DATE RANGE
            mat_value = selected_phase.material_logs.filter(
                date__range=[start_date, end_date]
            ).aggregate(
                total=Sum(ExpressionWrapper(
                    F('quantity_used') * F('material__cost_per_unit'),
                    output_field=DecimalField(max_digits=15, decimal_places=2)
                ))
            )['total'] or Decimal('0.00')

            # 2. FILTER LABOUR BY DATE RANGE
            labour_logs = selected_phase.attendance_logs.filter(
                date__range=[start_date, end_date]
            )
            labour_value = sum((log.daily_wage for log in labour_logs), Decimal('0.00'))

            # 3. GRAND TOTAL
            grand_total = mat_value + labour_value + extra_costs

            assignment = ProjectContractor.objects.get(
                contractor=request.user, 
                project=selected_phase.project
            )

            # 4. CREATE DETAILED AUDIT TRAIL
            detailed_desc = (
                f"PERIOD: {start_date} to {end_date}\n"
                f"PHASE: {selected_phase.phase_name}\n"
                f"--- AUTO-CALCULATED ---\n"
                f"Material Value: ${mat_value:,.2f}\n"
                f"Labour Wages:   ${labour_value:,.2f}\n"
                f"Contractor Fee: ${extra_costs:,.2f}\n"
                f"-----------------------\n"
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

        messages.success(request, f"Invoice for {start_date} to {end_date} submitted successfully.")
        return redirect('contractors:contractors_home')

    return render(request, 'contractors/submit_invoice.html', {'phases': phases})

from django.http import JsonResponse
from decimal import Decimal

@login_required
def get_phase_costs(request):
    phase_id = request.GET.get('phase_id')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if not all([phase_id, start_date, end_date]):
        return JsonResponse({'mat_cost': 0, 'lab_cost': 0})

    selected_phase = get_object_or_404(ProjectPhase, id=phase_id)

    # 1. Material Value within dates
    mat_cost = selected_phase.material_logs.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        total=Sum(ExpressionWrapper(
            F('quantity_used') * F('material__cost_per_unit'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        ))
    )['total'] or Decimal('0.00')

    # 2. Labour Wages within dates
    labour_logs = selected_phase.attendance_logs.filter(
        date__range=[start_date, end_date]
    )
    lab_cost = sum((log.daily_wage for log in labour_logs), Decimal('0.00'))

    return JsonResponse({
        'mat_cost': float(mat_cost),
        'lab_cost': float(lab_cost),
        'total': float(mat_cost + lab_cost)
    })