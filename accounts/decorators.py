from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def hospital_staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the Hospital Portal.")
            return redirect('accounts:login')
        
        profile = getattr(request.user, 'profile', None)
        if request.user.is_superuser or (profile and profile.is_hospital_staff):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Access restricted: Hospital or rescue staff privileges required.")
        return redirect('core:home')
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with administrator credentials.")
            return redirect('accounts:login')
        
        profile = getattr(request.user, 'profile', None)
        if request.user.is_superuser or (profile and profile.is_admin):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Access restricted: Administrator privileges required.")
        return redirect('core:home')
    return _wrapped_view
