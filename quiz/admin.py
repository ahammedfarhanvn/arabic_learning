from django.contrib import admin
from .models import Category, Question, UserProgress, UserQuestionAttempt

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category', 'correct_answer')
    
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_category', 'current_level', 'score')


admin.site.register(Category)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserProgress, UserProgressAdmin)
# admin.site.register(UserAnswer, UserAnswerAdmin)
admin.site.register(UserQuestionAttempt)




