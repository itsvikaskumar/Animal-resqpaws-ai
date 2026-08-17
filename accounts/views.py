from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileUpdateForm
from .models import UserProfile

def user_register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data.get('role', 'CITIZEN')
            profile.phone = form.cleaned_data.get('phone', '')
            if profile.role == 'HOSPITAL_STAFF':
                profile.affiliated_hospital = form.cleaned_data.get('hospital')
            profile.save()

            login(request, user)
            messages.success(request, f"Welcome to ResQPaws AI, {user.username}! Your account is active.")
            
            if profile.is_hospital_staff:
                return redirect('hospitals:dashboard')
            return redirect('rescue:report_animal')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Check redirect according to role
            profile = getattr(user, 'profile', None)
            if user.is_superuser or (profile and profile.is_admin):
                return redirect('analytics:admin_dashboard')
            elif profile and profile.is_hospital_staff:
                return redirect('hospitals:dashboard')
            else:
                return redirect('rescue:user_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('core:home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserProfileUpdateForm(instance=profile, initial=initial)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})
