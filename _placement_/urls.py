from django.contrib import admin
from django.urls import path
from project_campus import settings
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('materials/', views.materials, name='materials'),
      path('assessments/', views.assessments, name='assessments'),
    path('notice/<str:paper_code>/', views.notice, name='notice'),
    path('test/<str:paper_code>/', views.test, name='test'),
    path('result/<str:paper_code>/', views.result, name='result'),
    path('notice/<str:paper_code>/', views.notice, name='notice'),
    path('test/<str:paper_code>/', views.test, name='test'),
    path('result/<str:paper_code>/', views.result, name='result'),
    path('about/', views.about, name='about'),
    path('batch/', views.batch, name='batch'),
    path('test-mistakes/<str:paper_code>/', views.test_mistakes, name='test_mistakes'),
    path('test-mistakes/', views.test_mistakes, name='test_mistakes_all'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
        template_name='index_files/change_password.html',
        success_url='/',
    ), name='change_password'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='index_html/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='index_html/logout.html'), name='logout'),
    path('get_sections/', views.get_sections, name='get_sections'),
    path('refresh-dsa-count/', views.refresh_dsa_count, name='refresh_dsa_count'),
      path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)