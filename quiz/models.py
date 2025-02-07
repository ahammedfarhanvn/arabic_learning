from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE 
from django.db.models import F, Count


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Novice', 'Novice'),
        ('Beginner', 'Beginner'),
        ('Competent', 'Competent'),
        ('Proficient', 'Proficient'),
        ('Expert', 'Expert'),
    ]
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('Novice', 'Novice'),
        ('Beginner', 'Beginner'),
        ('Competent', 'Competent'),
        ('Proficient', 'Proficient'),
        ('Expert', 'Expert'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])

    def __str__(self):
        return self.question_text

from django.db import models
from django.contrib.auth.models import User

class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_category = models.CharField(max_length=100, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    score = models.IntegerField(default=0)
    completed_categories = models.JSONField(default=list, blank=True)  # Default empty list

    def __str__(self):
        return f"{self.user.username} Progress"
        
    #def __str__(self):
    #    return f"{self.user.username} - {self.current_category} (Level {self.current_level})"


# Track user's progress at the question level
class UserQuestionAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    level = models.IntegerField(default=1) # Current level within the category
    is_correct = models.BooleanField(default=False)  # Tracks if the user answered correctly

    class Meta:
        unique_together = ('user', 'question')  # Prevent duplicate attempts for the same question

    def __str__(self):
        return f"{self.user.username} - {self.question} - {'Correct' if self.is_correct else 'Wrong'}"

