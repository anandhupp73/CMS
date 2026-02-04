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
        # We take the actual amount being paid (usually invoice.amount)
        form_amount = Decimal(request.POST.get('amount', invoice.amount)) 
        
        with transaction.atomic():
            # 1. Create the payment record for audit
            Payment.objects.create(
                invoice=invoice,
                paid_amount=form_amount,
                mode=mode
            )
            
            # 2. Update Project Budget 
            # In a real system, the 'Total Impact' is the Invoice Amount.
            # Materials were already added to this amount in the contractor view.
            project.budget -= form_amount
            project.save()

            # 3. Finalize Invoice
            invoice.status = 'PAID'
            invoice.save()
            
        messages.success(request, f"Payment of ${form_amount} processed. Project budget updated.")
        return redirect('finance:accountant_dashboard')

    return render(request, 'finance/record_payment.html', {'invoice': invoice})