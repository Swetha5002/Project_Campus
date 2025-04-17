from django.contrib import admin
from .models import User, StudentResults, PlacementStories, Class

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'batch_year', 'date_joined')
    search_fields = ('username', 'email', 'batch_year')

@admin.register(StudentResults)
class StudentResultsAdmin(admin.ModelAdmin):
    list_display = ('user', 'test_code', 'test_title', 'percentage', 'status')
    search_fields = ('test_code', 'test_title', 'user__username')
    list_filter = ('status', 'date_of_exam')

@admin.register(PlacementStories)
class PlacementStoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'package', 'placement_year')
    search_fields = ('name', 'company')
    list_filter = ('placement_year',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch_year', 'created_at')
    search_fields = ('name', 'batch_year')

# Customize the admin site
admin.site.site_header = "VCET Admin Panel"
admin.site.site_title = "VCET Admin"
admin.site.index_title = "Welcome to the VCET Admin Panel"