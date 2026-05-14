from django import forms
from .models import Question

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()



class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'level']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Question Text'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correct Answer'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Level'}),
        }

        
class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Select Excel file')
    
# class UploadCSVForm(forms.Form):
#     csv_file = forms.FileField(label='Select CSV file')
