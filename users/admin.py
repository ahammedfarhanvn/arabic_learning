from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile


# Inline for displaying Profile alongside User in the admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# Custom UserAdmin to include Profile
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    # Customize the list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


# Unregister the default User model and re-register with the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Register Profile as a standalone model (optional, for management outside User admin)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')
    search_fields = ('user__username', 'user__email')