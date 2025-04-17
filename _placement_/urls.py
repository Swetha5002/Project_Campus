from django.contrib import admin
from django.urls import path
from project_campus import settings
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Use built-in Django admin
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('materials/', views.materials, name='materials'),
    path('assessments/', views.assessments, name='assessments'),
    path('about/', views.about, name='about'),
    path('class/<int:batch_year>/', views.class_users, name='class_users'),
    path('class/details/<int:batch_year>/', views.class_details, name='class_details'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
        template_name='index_files/change_password.html',
        success_url='/',
    ), name='change_password'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='index_html/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='index_html/logout.html'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)