from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import*
# from .forms import ExcelUploadForm
from .models import UserProgress
from users.models import Profile  
from .models import UserProgress 
from django.core.files.storage import FileSystemStorage
import pandas as pd
from .forms import UploadExcelForm

@login_required(login_url='users:login')
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
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
            'profile': profile,
        }
        
        return render(request, 'quiz/dashboard.html', context)
    
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error in dashboard view: {e}")
        return render(request, 'quiz/error.html', {'error': 'An error occurred in the dashboard.'})


@login_required
def quiz_view(request, category, level):
    profile = Profile.objects.filter(user=request.user).first()
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
        'profile': profile,
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
    profile = Profile.objects.filter(user=request.user).first()
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
    return render(request, 'quiz/import_questions.html',{'profile':profile})

def add_questions(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            if not excel_file.name.endswith(('.xls', '.xlsx')):
                messages.error(request, 'This is not an Excel file.')
                return redirect('quiz:add_questions')

            try:
                # Read the Excel file
                df = pd.read_excel(excel_file, engine='openpyxl')  # Use 'openpyxl' for .xlsx
                df = df.fillna('')  # Fill NaN values with empty strings
                
                for _, row in df.iterrows():
                    try:
                        # Extract values safely
                        category = str(row.get('category', '')).strip()
                        question_text = str(row.get('question_text', '')).strip()
                        option_a = str(row.get('option_a', '')).strip()
                        option_b = str(row.get('option_b', '')).strip()
                        option_c = str(row.get('option_c', '')).strip()
                        option_d = str(row.get('option_d', '')).strip()
                        correct_answer = str(row.get('correct_answer', '')).strip()
                        level = str(row.get('level', '0')).strip()
                        
                        # Validate and convert level
                        level = int(level) if level.isdigit() else 0

                        # Save question to the database
                        Question.objects.create(
                            category=category,
                            question_text=question_text,
                            option_a=option_a,
                            option_b=option_b,
                            option_c=option_c,
                            option_d=option_d,
                            correct_answer=correct_answer,
                            level=level
                        )
                    except Exception as e:
                        messages.error(request, f"Error processing row: {row.to_dict()}. Error: {e}")
                        continue  # Skip this row

                messages.success(request, 'Questions imported successfully!')
                return redirect('quiz:question_list')

            except Exception as e:
                messages.error(request, f"Error reading Excel file: {e}")
                return redirect('quiz:add_questions')

    else:
        form = UploadExcelForm()

    return render(request, 'quiz/add_questions.html', {'form': form})

def add_question(request):
    if request.method == "POST":
        # Handle form submission for adding a single question
        category = request.POST.get('category')
        question_text = request.POST.get('question_text')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_answer = request.POST.get('correct_answer')
        level = request.POST.get('level')
        if category and question_text and option_a and option_b and option_c and option_d and correct_answer and level.isdigit():
            Question.objects.create(
                category=category,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                level=int(level)
            )
            return redirect('quiz:question_list')

        # Handle file upload
        uploaded_file = request.FILES.get('question_file')
        if uploaded_file:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.url(filename)

            # Process the Excel file
            try:
                df = pd.read_excel(uploaded_file_path[1:], engine='openpyxl')
                df = df.fillna('')
                
                for _, row in df.iterrows():
                    if len(row) >= 8:  # Ensure there are enough columns
                        category = row[0]
                        question_text = row[1]
                        option_a = row[2]
                        option_b = row[3]
                        option_c = row[4]
                        option_d = row[5]
                        correct_answer = row[6]
                        level = row[7]
                        if str(level).isdigit():  # Ensure level is a valid number
                            Question.objects.create(
                                category=category,
                                question_text=question_text,
                                option_a=option_a,
                                option_b=option_b,
                                option_c=option_c,
                                option_d=option_d,
                                correct_answer=correct_answer,
                                level=int(level)
                            )
            except Exception as e:
                messages.error(request, f"Error reading Excel file: {e}")
                return redirect('quiz:add_question')

            return redirect('quiz:question_list')

    return render(request, 'quiz/add_question.html')



# def add_questions(request):
#     if request.method == 'POST':
#         form = UploadCSVForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES['csv_file']
            
#             if not csv_file.name.endswith('.csv'):
#                 messages.error(request, 'This is not a CSV file.')
#                 return redirect('quiz:add_customers')

#             # Read and decode the CSV file
#             decoded_file = csv_file.read().decode('utf-8')
#             io_string = io.StringIO(decoded_file)
#             csv_reader = csv.reader(io_string, delimiter=',')

#             next(csv_reader, None)  # Skip the header row if it exists

#             for row in csv_reader:
#                 try:
#                     # Extract values from row
#                     category, question_text, option_a, option_b, option_c, option_d, correct_answer, level = row

#                     # Clean and convert level safely
#                     level = level.strip()  # Remove extra spaces
#                     level = int(level) if level.isdigit() else 0  # Convert if it's a number, else set to 0

#                     # Save question to the database
#                     Question.objects.create(
#                         category=category,
#                         question_text=question_text,
#                         option_a=option_a,
#                         option_b=option_b,
#                         option_c=option_c,
#                         option_d=option_d,
#                         correct_answer=correct_answer,
#                         level=level  
#                     )

#                 except ValueError:
#                     messages.error(request, f"Invalid level value: {level}. Row skipped.")
#                     continue  # Skip this row and move to the next one
#                 except Exception as e:
#                     messages.error(request, f"Error processing row: {row}. Error: {e}")
#                     continue  # Skip this row and move to the next one

#             messages.success(request, 'Questions imported successfully!')
#             return redirect('quiz:question_list')

#     else:
#         form = UploadCSVForm()

#     return render(request, 'quiz/add_questions.html', {'form': form})


# def add_question(request):
#     if request.method == "POST":
#         # Handle form submission for adding a single customer
#         category = request.POST.get('category')
#         question_text = request.POST.get('question_text')
#         option_a = request.POST.get('option_a')
#         option_b = request.POST.get('option_b')
#         option_c = request.POST.get('option_c')
#         option_d = request.POST.get('option_d')
#         correct_answer = request.POST.get('correct_answer')
#         level = request.POST.get('level')
#         if category and question_text and option_a and option_b and option_c and option_d and correct_answer and level.isdigit():
#             Question.objects.create(
#                                 category=category,
#                                 question_text=question_text,
#                                 option_a=option_a,
#                                 option_b=option_b,
#                                 option_c=option_c,
#                                 option_d=option_d,
#                                 correct_answer=correct_answer,
#                                 level=int(level)
#                             )
#             return redirect('quiz:question_list')

#         # Handle file upload
#         uploaded_file = request.FILES.get('question_file')
#         if uploaded_file:
#             fs = FileSystemStorage()
#             filename = fs.save(uploaded_file.name, uploaded_file)
#             uploaded_file_path = fs.url(filename)

#             # Process the CSV file
#             with open(uploaded_file_path[1:], newline='') as csvfile:  # Remove leading '/' from URL
#                 reader = csv.reader(csvfile)
#                 for row in reader:
#                     if len(row) >= 8:  # Ensure there are enough columns
#                         category = row[0]
#                         question_text = row[1]
#                         option_a = row[2]
#                         option_b = row[3]
#                         option_c = row[4]
#                         option_d = row[5]
#                         correct_answer = row[6]
#                         level = row[7]
#                         if level.isdigit():  # Ensure balance is a valid number
#                             Question.objects.create(
#                                 category=category,
#                                 question_text=question_text,
#                                 option_a=option_a,
#                                 option_b=option_b,
#                                 option_c=option_c,
#                                 option_d=option_d,
#                                 correct_answer=correct_answer,
#                                 level=int(level)
#                             )

#             return redirect('quiz:question_list')

#     return render(request, 'quiz/add_question.html')

def question_list(request):
    questions = Question.objects.all()
    return render(request, 'quiz/question_list.html', {'questions': questions})
