from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import UserRegisterForm
from workouts.models import Workout, SavedWorkout
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')  
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user_workouts = Workout.objects.filter(author=request.user).order_by('-created_at')
    
    saved_workouts = SavedWorkout.objects.filter(user=request.user).order_by('-saved_at')
    
    context = {
        'user_workouts': user_workouts,
        'saved_workouts': saved_workouts
    }
    
    return render(request, 'users/profile.html', context)

def custom_logout(request):
    """Custom logout view that works with both GET and POST requests"""
    logout(request)
    
    return render(request, 'users/logout.html')

def get_csrf_token(request):
    """Return CSRF token for API use"""
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

@require_POST
@csrf_protect
def api_login(request):
    """API endpoint for login"""
    # Debug information
    print("API Login called")
    print(f"POST data: {request.POST}")
    
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    # Validate input
    if not username:
        return JsonResponse({
            'success': False, 
            'errors': ['Username is required']
        }, status=400)
        
    if not password:
        return JsonResponse({
            'success': False, 
            'errors': ['Password is required']
        }, status=400)
    
    # Authenticate user
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'redirect': '/',  # Default redirect to home
            'username': user.username
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': ['Invalid username or password']
        }, status=400)

@require_POST
def api_logout(request):
    """API endpoint for logout"""
    logout(request)
    return JsonResponse({
        'success': True,
        'redirect': '/'
    })

@require_POST
def api_register(request):
    """API endpoint for user registration"""
    from .forms import UserRegisterForm
    
    form = UserRegisterForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)  
        return JsonResponse({
            'success': True,
            'redirect': '/',
            'username': user.username
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)