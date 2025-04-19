from datetime import timezone
from datetime import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from _placement_ import Scraper
from _placement_.Scraper import update_user_dsa_count
from .models import MistakenQuestion, User, StudentResults, PlacementStories, Section  # Added Class model and Section
from .forms import PaperCodeForm, UserForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponse, JsonResponse
import csv
from django.contrib.auth.views import PasswordResetView
from django.db import IntegrityError
from django.db.models import F, Q
from django.core.paginator import Paginator
from django.db import models  # Add this import

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
        
        score = 0
        mistaken_questions = []
        
        # Calculate score and collect mistaken questions
        for question in paper.questions.all():
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer == question.correct_option:
                score += question.mark
            else:
                mistaken_questions.append(
                    MistakenQuestion(
                        user=request.user,
                        question=question,
                        test_code=paper_code,
                        selected_option=user_answer or 'Not answered',
                        correct_option=question.correct_option
                    )
                )
        
        # Calculate result metrics
        time_taken = int(request.POST.get('time_taken', 0))
        total_marks = paper.total_marks or 0
        percentage = (score / total_marks) * 100 if total_marks > 0 else 0
        malpractice = request.POST.get('malpractice', 'false') == 'true'

        # Create or update StudentResults
        result_obj, created = StudentResults.objects.update_or_create(
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
        
        # Associate and save mistaken questions
        if mistaken_questions:
            for mistake in mistaken_questions:
                mistake.student_result = result_obj
            MistakenQuestion.objects.bulk_create(mistaken_questions)

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
    return redirect('home')

@login_required
def batch(request):
    # Get the current user's batch
    user_batch = request.user.batch

    if not user_batch:
        messages.error(request, "You are not assigned to any batch.")
        return redirect('home')

    # Fetch all batchmates
    batchmates = User.objects.filter(batch=user_batch).order_by('name')

    # Sorting logic
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'dsa':
        batchmates = batchmates.order_by('-dsa_problem_solved_count', 'name')
    elif sort_by == 'percentage':
        batchmates = batchmates.order_by('-average_percentage', 'name')

    # Fetch top 20 performers based on DSA count and average percentage
    top_20_users = batchmates.order_by(
        F('dsa_problem_solved_count').desc(nulls_last=True),
        F('average_percentage').desc(nulls_last=True)
    )[:20]

    # Pagination for batchmates
    paginator = Paginator(batchmates, 10)  # Show 10 batchmates per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context for the template
    context = {
        'batchmates': page_obj,
        'top_20_users': top_20_users,
        'sort_by': sort_by,
        'total_students': batchmates.count(),
        'avg_dsa': batchmates.aggregate(avg_dsa=models.Avg('dsa_problem_solved_count'))['avg_dsa'] or 0,
        'top_dsa_user': batchmates.order_by('-dsa_problem_solved_count').first(),
        'top_dsa_count': batchmates.aggregate(max_dsa=models.Max('dsa_problem_solved_count'))['max_dsa'] or 0,
        'top_percentage_user': batchmates.order_by('-average_percentage').first(),
        'top_percentage': batchmates.aggregate(max_percentage=models.Max('average_percentage'))['max_percentage'] or 0,
    }

    return render(request, 'index_html/batch.html', context)

@login_required
def section(request):
    # Get the current user's section
    user_section = request.user.section

    if not user_section:
        messages.error(request, "You are not assigned to any section.")
        return redirect('home')

    # Fetch all sectionmates
    sectionmates = User.objects.filter(section=user_section).order_by('name')

    # Sorting logic
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'dsa':
        sectionmates = sectionmates.order_by('-dsa_problem_solved_count', 'name')
    elif sort_by == 'percentage':
        sectionmates = sectionmates.order_by('-average_percentage', 'name')

    # Fetch top 10 performers based on DSA count and average percentage
    top_10_users = sectionmates.order_by(
        F('dsa_problem_solved_count').desc(nulls_last=True),
        F('average_percentage').desc(nulls_last=True)
    )[:10]

    # Pagination for sectionmates
    paginator = Paginator(sectionmates, 10)  # Show 10 sectionmates per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context for the template
    context = {
        'sectionmates': page_obj,
        'top_10_users': top_10_users,
        'sort_by': sort_by,
        'total_students': sectionmates.count(),
        'avg_dsa': sectionmates.aggregate(avg_dsa=models.Avg('dsa_problem_solved_count'))['avg_dsa'] or 0,
        'top_dsa_user': sectionmates.order_by('-dsa_problem_solved_count').first(),
        'top_dsa_count': sectionmates.aggregate(max_dsa=models.Max('dsa_problem_solved_count'))['max_dsa'] or 0,
        'top_percentage_user': sectionmates.order_by('-average_percentage').first(),
        'top_percentage': sectionmates.aggregate(max_percentage=models.Max('average_percentage'))['max_percentage'] or 0,
    }

    return render(request, 'index_html/section.html', context)

def get_sections(request):
    batch_id = request.GET.get('batch_id')
    sections = Section.objects.filter(batch_id=batch_id).values('id', 'name')
    return JsonResponse({'sections': list(sections)})

def test_mistakes(request, paper_code):
    if not request.user.is_authenticated:
        return redirect('login')
    
    paper = get_object_or_404(QuestionPaper, paper_code=paper_code)
    mistaken_questions = MistakenQuestion.objects.filter(
        user=request.user,
        test_code=paper_code
    ).select_related('question')
    
    context = {
        'paper': paper,
        'mistaken_questions': mistaken_questions,
    }
    return render(request, 'test_activity/test_mistakes.html', context)


def get_sections(request):
    batch_id = request.GET.get('batch_id')
    sections = Section.objects.filter(batch_id=batch_id).values('id', 'name')
    return JsonResponse({'sections': list(sections)})


@login_required
def refresh_dsa_count(request):
    """
    API endpoint to manually refresh DSA count for current user
    """
    try:
        count = update_user_dsa_count(request.user)
        return JsonResponse({
            'success': True,
            'count': count,
            'message': 'DSA count updated successfully!',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating DSA count: {str(e)}'
        }, status=500)

