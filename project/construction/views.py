from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'construction/pm_dashboard.html')

def add_project(request):
    return render(request, 'construction/add_project.html')