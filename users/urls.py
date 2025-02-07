from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('check_username/', views.check_username, name='check_username'),  # Username check (AJAX)
    path('register/', views.register_view, name='register'),
    path('settings/', views.edit_profile_view, name='profile_settings'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
]