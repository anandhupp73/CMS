from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from construction.models import ProjectPhase, Project

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
def submit_invoice(request):
    return render(request, 'contractors/submit_invoice.html')

@login_required
def work_logs(request):
    # Logic for daily logs
    return render(request, 'contractors/work_logs.html')