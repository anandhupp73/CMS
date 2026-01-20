from django.shortcuts import redirect

def role_required(role_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role and request.user.role.name == role_name:
                return view_func(request, *args, **kwargs)
            return redirect('dashboard')
        return wrapper
    return decorator
