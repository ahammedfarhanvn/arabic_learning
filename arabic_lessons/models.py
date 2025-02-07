from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    difficulty_level = models.CharField(
        max_length=50,
        choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")],
    )
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_locked = models.BooleanField(default=True)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.title} - {self.module.title}"


class Exercise(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    question = models.CharField(max_length=500)
    exercise_type = models.CharField(
        max_length=50,
        choices=[
            ("multiple_choice", "Multiple Choice"),
            ("fill_in_the_blank", "Fill in the Blank"),
            ("drag_and_drop", "Drag and Drop"),
        ]
    )
    answer_choices = models.JSONField(default=list, blank=True)
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)
    points = models.IntegerField()

    def __str__(self):
        return f"Exercise: {self.question}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress', blank=True, null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress', blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', blank=True, null=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='progress', blank=True, null=True)
    score = models.IntegerField(default=0)
    completion_time = models.DateTimeField(blank=True, null=True)
    attempts = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Progress for {self.user.username}"


class Badge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='badge_images/', blank=True, null=True)
    criteria = models.JSONField(default=dict)
    users = models.ManyToManyField(User, related_name="badges")

    def __str__(self):
        return self.name
        

class UserProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    current_category = models.CharField(max_length=255, blank=True, null=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Progress"