from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'difficulty_level')
    list_filter = ('category', 'difficulty_level')
    search_fields = ('title', 'description')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order')
    search_fields = ('title', 'course__title')
    ordering = ('order',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module', 'is_locked', 'order')
    list_filter = ('module', 'is_locked')
    search_fields = ('title', 'content')
    ordering = ('order',)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'lesson', 'exercise_type', 'points')
    list_filter = ('exercise_type', 'lesson__module__course')
    search_fields = ('question',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'current_category', 'score')
    list_filter = ('current_category',)
    search_fields = ('user__username', 'current_category')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')