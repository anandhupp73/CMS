from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from contractors.models import *
from .models import *
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from django.db import transaction

def is_acc(user):
    return user.role and user.role.name == 'Accountant'

@login_required
@user_passes_test(is_acc)
def home(request):
    pending_payments = Invoice.objects.filter(status='APPROVED').order_by('-created_at')
    # History of completed payments
    payment_history = Payment.objects.all().select_related('invoice', 'invoice__contractor__contractor', 'invoice__project').order_by('-paid_date')
    
    return render(request, 'finance/accountant_dashboard.html', {
        'pending_payments': pending_payments,
        'payment_history': payment_history,
    })
    
@login_required
@user_passes_test(is_acc)
def record_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    project = invoice.project

    if request.method == 'POST':
        mode = request.POST.get('mode')
        # Ensure the amount from the form is treated as a Decimal
        form_amount = Decimal(request.POST.get('amount', 0)) 
        
        # Use an atomic transaction so if the budget save fails, 
        # the invoice doesn't mark as PAID by mistake.
        with transaction.atomic():
            # 1. Calculate Material Costs for this specific phase
            material_val = invoice.phase.material_logs.aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F('quantity_used') * F('material__cost_per_unit'),
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    )
                )
            )['total'] or Decimal('0.00')

            # 2. Total amount to reduce from the remaining budget
            total_deduction = form_amount + material_val

            # 3. Create the payment record
            Payment.objects.create(
                invoice=invoice,
                paid_amount=form_amount,
                mode=mode
            )
            
            # 4. Update Project Budget (Deduction logic)
            project.budget -= total_deduction
            project.save()

            # 5. Finalize Invoice
            invoice.status = 'PAID'
            invoice.save()
            
        messages.success(request, f"Success! ${form_amount} paid and ${material_val} material value settled.")
        return redirect('finance:accountant_dashboard')

    return render(request, 'finance/record_payment.html', {'invoice': invoice})