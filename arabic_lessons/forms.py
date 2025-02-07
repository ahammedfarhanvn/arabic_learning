from django import forms
from .models import Lesson, Exercise

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'level']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter lesson title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write lesson content...'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter level (e.g., 1, 2, 3)'}),
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['question', 'answer', 'question_type', 'options']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the question'}),
            'answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the correct answer'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'options': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated options (for MCQ)'}),
        }