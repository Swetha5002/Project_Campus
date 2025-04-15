from django.shortcuts import render

# Create your views here.

def home (request):
    return render(request, 'index_html/home.html')

def profile (request):
    return render(request, 'index_html/profile.html')