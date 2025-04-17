from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, StudentResults, PlacementStories, Class  # Added Class model
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponse
import csv

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Signup successful! Please log in.')
            return redirect('home')
    else:
        form = UserForm()
    return render(request, 'index_html/signup.html', {'form': form})

def home(request):
    placement_stories = PlacementStories.objects.all()
    context = { 'placement_stories': placement_stories}
    return render(request, 'index_html/home.html', context)

@login_required  
def profile(request):
    return render(request, 'index_html/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserForm(instance=request.user)
    return render(request, 'index_html/edit_profile.html', {'form': form})

def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'index_html/view_profile.html', {'user': user})

def materials(request):
    return render(request, 'index_html/materials.html')

@login_required
def assessments(request):
    return render(request, 'index_html/assessments.html')

@login_required
def admin_dashboard(request):
    raise Http404("This feature has been removed.")

@login_required
def manage_classes(request):
    raise Http404("This feature has been removed.")

def about(request):
    return render(request, 'index_html/about.html')

@login_required
def class_users(request, batch_year):
    users = User.objects.filter(batch_year=batch_year)
    return render(request, 'index_html/class_users.html', {'users': users, 'batch_year': batch_year})

@login_required
def class_details(request, batch_year):
    users = User.objects.filter(batch_year=batch_year)
    class_name = f"Batch {batch_year}"
    start_year = batch_year
    end_year = batch_year + 4  # Assuming a 4-year program
    student_count = users.count()
    return render(request, 'index_html/class_details.html', {
        'class_name': class_name,
        'start_year': start_year,
        'end_year': end_year,
        'student_count': student_count,
        'users': users,
    })
