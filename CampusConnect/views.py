from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return render(request, 'home.html')

def myposts(request):
    return render(request, 'myposts.html')

def profile(request):
    return HttpResponse("profile page")

def helpothers(request):
    return render(request, 'helpothers.html')

def dashboard(request):
    return render(request, 'dashboard.html')    