from datetime import timezone
from datetime import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, StudentResults, PlacementStories, Section  # Added Class model and Section
from .forms import PaperCodeForm, UserForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponse, JsonResponse
import csv
from django.contrib.auth.views import PasswordResetView
from django.db import IntegrityError

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])  # Set the password
                user.save()
                messages.success(request, 'Signup successful! Please log in.')
                return redirect('login')
            except IntegrityError as e:
                if 'email' in str(e):
                    form.add_error('email', 'This email is already registered. Please use a different email address.')
                elif 'username' in str(e):
                    form.add_error('username', 'This username is already taken. Please choose a different one.')
                else:
                    messages.error(request, 'An error occurred during signup. Please try again.')
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



def notice(request, paper_code):
    """
    Displays the test notice page and checks if the user is eligible to take the test.
    """
    paper = get_object_or_404(QuestionPaper, paper_code=paper_code)

    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to access the test.')
        return redirect('login')

    if StudentResults.objects.filter(user=request.user, test_code=paper_code, attended=True).exists():
        messages.warning(request, 'You have already attended this test.')
        return redirect('/#assessments')

    return render(request, 'test_activity/notice.html', {'paper': paper})

from django.shortcuts import render, get_object_or_404
from .models import StudentResults, QuestionPaper 

from django.utils import timezone
from .models import QuestionPaper  # Make sure this is imported


def notice(request, paper_code):
    """
    Displays the test notice page and checks if the user is eligible to take the test.
    """
    paper = get_object_or_404(QuestionPaper, paper_code=paper_code)

    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to access the test.')
        return redirect('login')

    if StudentResults.objects.filter(user=request.user, test_code=paper_code, attended=True).exists():
        messages.warning(request, 'You have already attended this test.')
        return redirect('/#assessments')

    return render(request, 'test_activity/notice.html', {'paper': paper})

from django.shortcuts import render, get_object_or_404
from .models import StudentResults, QuestionPaper 

from django.utils import timezone
from .models import QuestionPaper  # Make sure this is imported

@login_required
def assessments(request):
    if request.method == 'GET' and 'paper_code' in request.GET:
        paper_code = request.GET.get('paper_code')
        try:
            paper = QuestionPaper.objects.get(paper_code=paper_code)
            if StudentResults.objects.filter(user=request.user, test_code=paper_code, attended=True).exists():
                messages.warning(request, 'You have already taken this test')
                return redirect('assessments')
            request.session['paper_code'] = paper_code
            return redirect('notice', paper_code=paper_code)
        except QuestionPaper.DoesNotExist:
            messages.error(request, 'Invalid test code')
    
    return render(request, 'index_html/assessments.html')

def test(request, paper_code):
    paper = get_object_or_404(QuestionPaper, paper_code=paper_code)
    attend = StudentResults.objects.filter(user=request.user, test_code=paper_code).exists()
    context = {
        'attend': attend,
        'paper': paper,
        'questions': paper.questions.all().order_by("?"), 
    }
    print(attend)
    return render(request, 'test_activity/test.html', context)

def result(request, paper_code):
    paper = get_object_or_404(QuestionPaper, paper_code=paper_code)

    if request.method == 'POST':
        if request.user.is_superuser:
            return redirect('home')
        score = sum(
            question.mark
            for question in paper.questions.all()
            if request.POST.get(f'question_{question.id}') == question.correct_option
        )
        time_taken = int(request.POST.get('time_taken', 0))
        total_marks = paper.total_marks or 0
        percentage = (score / total_marks) * 100 if total_marks > 0 else 0
        malpractice = request.POST.get('malpractice', 'false') == 'true'

        StudentResults.objects.update_or_create(
            user=request.user,
            test_code=paper_code,
            defaults={
                'test_title': paper.paper_title,
                'percentage': percentage,
                'attended': True,
                'status': 'Malpractice' if malpractice else 'Completed',
                'date_of_exam': timezone.now().date(),
                'time': timezone.now().time(),
            }
        )

        context = {
            'paper': paper,
            'score': score,
            'total_marks': total_marks,
            'percentage': percentage,
            'time_taken': time_taken,
            'malpractice': malpractice,
            'redirect_timeout': 7,
        }
        return render(request, 'test_activity/result.html', context)

    messages.error(request, 'Invalid request.')
    return redirect('index')

def batch(request):
    return render(request, 'index_html/batch.html')

def get_sections(request):
    batch_id = request.GET.get('batch_id')
    sections = Section.objects.filter(batch_id=batch_id).values('id', 'name')
    return JsonResponse({'sections': list(sections)})