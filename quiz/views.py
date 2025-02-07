from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Category, Question, UserQuestionAttempt, UserProgress
#import pandas as pd
from .forms import ExcelUploadForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProgress
from users.models import Profile  # Import the Profile model from the users app

from django.shortcuts import render
from .models import UserProgress  # Import your models
from django.contrib.auth.decorators import login_required

@login_required(login_url='users:login')
def dashboard(request):
    try:
        # Ensure user progress is correctly fetched
        user_progress, created = UserProgress.objects.get_or_create(user=request.user)

        # Check if current_category is None, which could cause the issue
        if user_progress.current_category is None:
            user_progress.current_category = 'Novice'  # Set a default value or handle as needed
            user_progress.save()  # Save the user progress if updated

        # Check if category list exists and user_progress.current_category is in it
        categories = ['Novice', 'Beginner', 'Competent', 'Proficient', 'Expert']
        
        if user_progress.current_category not in categories:
            raise ValueError("User's current category is invalid.")
        
        # Proceed with other logic
        # Add more processing as needed based on the existing logic in your dashboard view
        
        # Create context dictionary
        context = {
            'user_progress': user_progress,
            # Add any other context needed for the dashboard
        }
        
        return render(request, 'quiz/dashboard.html', context)
    
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error in dashboard view: {e}")
        return render(request, 'quiz/error.html', {'error': 'An error occurred in the dashboard.'})


@login_required
def quiz_view(request, category, level):
    """
    Display the question for the given category and level.
    Allow the user to progress to the next level only if they answer correctly.
    """
    # Get or create user progress
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)

    # Validate category access
    if category != user_progress.current_category or level > user_progress.current_level:
        return redirect('quiz:dashboard')

    # Fetch the question for the current level
    question_index = level - 1  # Adjust to match the level with question index
    questions = Question.objects.filter(category=category)

    # Ensure there are enough questions for the given level
    if question_index >= len(questions):
        return redirect('quiz:dashboard')  # No more questions available in this category

    question = questions[question_index]

    if request.method == 'POST':
        selected_answer = request.POST.get('answer')

        # Check if the answer is correct
        if selected_answer == question.correct_answer:
            # Update score and progress
            if level == user_progress.current_level:
                user_progress.score += 1
                user_progress.current_level += 1

                # Check if the current category is complete
                if user_progress.current_level > len(questions):
                    categories = ['Novice', 'Beginner', 'Competent', 'Proficient', 'Expert']
                    current_category_index = categories.index(user_progress.current_category)
                    if current_category_index + 1 < len(categories):
                        user_progress.current_category = categories[current_category_index + 1]
                        user_progress.current_level = 1
                user_progress.save()
            return redirect('quiz:quiz_view', category=user_progress.current_category, level=user_progress.current_level)

    context = {
        'category': category,
        'level': level,
        'question': question,
    }
    return render(request, 'quiz/quiz.html', context)

@login_required(login_url='login')
def category_detail(request, category):
    """Display levels for a selected category."""
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)
    levels = range(1, 51)  # Assume 50 levels per category
    levels_status = []

    # Fetch completed_categories and ensure it's a list
    completed_categories = user_progress.completed_categories

    # If completed_categories is None, initialize it as an empty list
    if not completed_categories:
        completed_categories = []

    # Determine the current level based on user progress
    if category in completed_categories:
        # If the category is completed, unlock all levels
        current_level = 50  # All levels unlocked
    elif user_progress.current_category == category:
        # If the user is currently working on this category
        current_level = user_progress.current_level
    else:
        # Locked category
        current_level = 0

    # Create level status for each level
    for level in levels:
        status = "unlocked" if level <= current_level else "locked"
        levels_status.append({
            "number": level,
            "status": status
        })

    # Safely retrieve the profile
    profile = Profile.objects.filter(user=request.user).first()

    context = {
        "category": category,
        "levels_status": levels_status,
        "profile": profile,
    }
    return render(request, "quiz/category_detail.html", context)

@login_required(login_url='login')
def import_questions(request):
    """Allows admin to import questions from an Excel file."""
    if request.method == "POST" and request.FILES["excel_file"]:
        file = request.FILES["excel_file"]

        # Handle Excel file import
        import openpyxl

        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            category, question_text, option_a, option_b, option_c, option_d, correct_answer, level = row
            Question.objects.create(
                category=category,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                level=level,
            )
        return JsonResponse({"success": True, "message": "Questions imported successfully!"})
    return render(request, 'quiz/import_questions.html')

