from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages

def role_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard_router')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


def logout_view(request):
    auth_logout(request)  
    return redirect('login')
