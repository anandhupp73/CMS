from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

@login_required
@role_required('Accountant')
def home(request):
    return render(request, 'finance/home.html')