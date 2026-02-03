from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from contractors.models import *
from .models import *
from django.contrib import messages

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
    
    if request.method == 'POST':
        mode = request.POST.get('mode')
        amount = request.POST.get('amount')
        
        # 1. Create the payment record
        Payment.objects.create(
            invoice=invoice,
            paid_amount=amount,
            mode=mode
        )
        
        # 2. Update the invoice status to PAID
        invoice.status = 'PAID'
        invoice.save()
        
        messages.success(request, f"Payment of ${amount} confirmed for Invoice #{invoice.id}")
        return redirect('finance:accountant_dashboard')

    return render(request, 'finance/record_payment.html', {'invoice': invoice})