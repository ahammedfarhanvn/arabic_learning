from django.urls import path
from . import views

app_name = 'arabic_lessons'

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/exercises/<int:exercise_id>/submit/',
         views.submit_exercise, name='submit_exercise'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('user_progress/', views.user_progress, name='user_progress'),
         
    
    #admin page urls
    path('lesson_list/', views.lesson_list_admin, name='lesson_list_admin'),
    path('create/', views.create_lesson, name='create_lesson'),
    path('<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('<int:lesson_id>/add_exercise/', views.add_exercise, name='add_exercise'),
]
