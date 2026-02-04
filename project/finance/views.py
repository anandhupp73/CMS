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
    # 1. Fetch the invoice by ID only (prevents generic 404)
    invoice = get_object_or_404(Invoice, id=invoice_id)
    project = invoice.project

    # 2. Status Guard: Ensure it was approved by PM
    if invoice.status != 'APPROVED':
        messages.error(request, f"Invoice #{invoice_id} is currently '{invoice.status}'. It must be APPROVED by the PM before payment.")
        return redirect('finance:finance_home')

    if request.method == 'POST':
        mode = request.POST.get('mode')
        # Get amount from form, fallback to invoice total
        try:
            form_amount = Decimal(request.POST.get('amount', invoice.amount))
        except:
            form_amount = invoice.amount
        
        # 3. Financial Guard: Check remaining budget
        if project.budget < form_amount:
            messages.error(request, f"Insufficient Budget! Available: ₹{project.budget}. Required: ₹{form_amount}")
            return redirect('finance:finance_home')

        with transaction.atomic():
            # Create Audit Trail
            Payment.objects.create(
                invoice=invoice,
                paid_amount=form_amount,
                mode=mode
            )
            
            # Update Project Finances
            project.budget -= form_amount
            project.save()

            # Finalize Status
            invoice.status = 'PAID'
            invoice.save()
            
        messages.success(request, f"Payment of ₹{form_amount} processed. Project budget updated.")
        return redirect('finance:finance_home')

    return render(request, 'finance/record_payment.html', {'invoice': invoice})