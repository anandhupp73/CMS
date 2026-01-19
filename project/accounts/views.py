from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from .forms import RoleLoginForm

def role_login(request):
    if request.method == 'POST':
        form = RoleLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            # Redirect based on role
            role = user.role
            if role == 'ADMIN':
                return redirect('/dashboard/')  # Admin dashboard
            elif role == 'PM':
                return redirect('/dashboard/')  # PM dashboard
            elif role == 'SUP':
                return redirect('/dashboard/')  # Supervisor dashboard
            elif role == 'CONT':
                return redirect('/dashboard/')  # Contractor dashboard
            elif role == 'ACC':
                return redirect('/dashboard/')  # Accountant dashboard
    else:
        form = RoleLoginForm()
    return render(request, 'registration/role_login.html', {'form': form})


def custom_logout(request):
    logout(request)  # log out the user
    return redirect('/login/')