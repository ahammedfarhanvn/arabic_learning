from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Category, Course, Module, Lesson, Exercise, UserProgress, Badge
from django.db.models import Sum

def course_list(request):
    categories = Category.objects.prefetch_related('courses')
    return render(request, 'arabic_lessons/course_list.html', {'categories': categories})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.order_by('order')
    return render(request, 'arabic_lessons/course_detail.html', {'course': course, 'modules': modules})


@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    exercises = lesson.exercises.all()
    return render(request, 'arabic_lessons/lesson_detail.html', {
        'lesson': lesson,
        'exercises': exercises,
        'course': course,
    })


@login_required
def submit_exercise(request, course_id, lesson_id, exercise_id):
    if request.method == "POST":
        exercise = get_object_or_404(Exercise, id=exercise_id, lesson__id=lesson_id, lesson__module__course__id=course_id)
        user_answer = request.POST.get('answer')
        is_correct = user_answer == exercise.correct_answer
        points_awarded = exercise.points if is_correct else 0

        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user, lesson=exercise.lesson, exercise=exercise
        )
        user_progress.score += points_awarded
        user_progress.attempts += 1
        user_progress.is_completed = is_correct
        user_progress.save()

        return JsonResponse({'is_correct': is_correct, 'points_awarded': points_awarded})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def leaderboard(request):
    """
    Displays a leaderboard showcasing top users based on their total points.
    """
    top_users = UserProgress.objects.values('user__username').annotate(
        total_points=Sum('score')
    ).order_by('-total_points')[:10]

    return render(request, 'arabic_lessons/leaderboard.html', {'top_users': top_users})

@login_required
def user_progress(request):
    """
    Displays the user's overall progress, including badges and scores.
    """
    progress = UserProgress.objects.filter(user=request.user)
    badges = Badge.objects.filter(users=request.user)
    return render(request, 'arabic_lessons/user_progress.html', {
        'progress': progress,
        'badges': badges,
    })


#admin arabic_lessons
@login_required
def lesson_list_admin(request):
    lessons = Lesson.objects.all().order_by('level')
    return render(request, 'arabic_lessons/lesson_list_admin.html', {'lessons': lessons})

@login_required
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('arabic_lessons:lesson_list')
    else:
        form = LessonForm()
    return render(request, 'arabic_lessons/create_lesson.html', {'form': form})

@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('arabic_lessons:lesson_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'arabic_lessons/create_lesson.html', {'form': form})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson.delete()
    messages.success(request, "Lesson deleted successfully!")
    return redirect('arabic_lessons:lesson_list')

@login_required
def add_exercise(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.lesson = lesson
            exercise.save()
            messages.success(request, "Exercise added successfully!")
            return redirect('arabic_lessons:lesson_list')
    else:
        form = ExerciseForm()
    return render(request, 'arabic_lessons/create_exercise.html', {'lesson': lesson, 'form': form})