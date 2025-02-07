from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from arabic_lessons.models import UserProgress
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('pass1')
        password2 = request.POST.get('pass2')
        profile_picture = request.FILES.get('profile_picture')

        # Check if passwords match
        if password1 != password2:
            return render(request, 'users/register.html', {
                'error': 'Passwords do not match', 
                'username': username, 
                'email': email
            })

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {
                'error': 'Username already exists', 
                'username': username, 
                'email': email
            })

        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Use default profile picture if none is uploaded
            if not profile_picture:
                profile_picture = "profile_pictures/default.png"

            # Create profile
            profile = Profile(user=user, profile_picture=profile_picture)
            profile.save()

            # Create UserProgress
            user_progress = UserProgress.objects.create(user=user, current_category='Novice', score=0)

            # Log the user in and redirect to the home page
            login(request, user)
            return redirect('users:home')

        except Exception as e:
            logger.error(f"Error during registration: {e}")  # Log the exact error
            return render(request, 'users/register.html', {
                'error': f"There was an error during registration: {e}"  # Show the exact error in the template
            })
    else:
        return render(request, 'users/register.html')


@csrf_exempt
def check_username(request):
    """
    Handles AJAX requests to check if a username already exists.
    """
    username = request.GET.get('username', None)
    if username:
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})


def login_view(request):
    """
    Handles user login.
    """
    if request.user.is_authenticated:
        return redirect('users:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('users:home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html', {'username': username})

    return render(request, 'users/login.html')


def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    return redirect('users:login')

@login_required(login_url='users:login')
def edit_profile_view(request):
    """
    Allows users to edit their profile, including uploading a profile picture.
    """
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')

        if profile_picture:
            try:
                logger.debug(f"Uploading file: {profile_picture.name}")
                # Save the uploaded profile picture
                profile.profile_picture = profile_picture
                profile.save()
                messages.success(request, "Profile updated successfully.")
            except Exception as e:
                logger.error(f"Error while updating profile picture: {e}")
                messages.error(request, f"Error while updating profile picture: {e}")
        else:
            messages.error(request, "No profile picture was uploaded.")

        return redirect('users:profile_settings')

    return render(request, 'users/edit_profile.html', {'profile': profile})

from django.templatetags.static import static

@login_required(login_url='users:login')
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Assign default profile picture URL if none exists
    if not profile.profile_picture:
        profile.profile_picture_url = static('images/default_avatar.png')
    else:
        profile.profile_picture_url = profile.profile_picture.url

    categories = ['Novice', 'Beginner', 'Competent', 'Proficient', 'Expert']

    try:
        # Fetch or create user progress
        user_progress, _ = UserProgress.objects.get_or_create(user=request.user)

        # Assign default category if `current_category` is None
        if not user_progress.current_category:
            user_progress.current_category = 'Novice'
            user_progress.save()
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        messages.error(request, "There was an issue with loading your profile or progress.")
        return render(request, 'users/error.html', {'error': f"Error: {e}"})

    # Generate category statuses
    category_status = []
    for category in categories:
        if user_progress.current_category == category:
            status = "current"
        elif categories.index(category) < categories.index(user_progress.current_category):
            status = "unlocked"
        else:
            status = "locked"
        category_status.append({"name": category, "status": status})

    context = {
        'category_status': category_status,
        'user_progress': user_progress,
        'profile': profile,
    }

    return render(request, 'users/home.html', context)