from django.shortcuts import render, redirect
from .models import Student
from django.contrib import messages
# Create your views here.

def home(request):
    return render(request, 'home.html')


def myposts(request):
    return render(request, 'myposts.html')


def profile(request):
    return render(request,"profile page")


def helpothers(request):
    return render(request, 'helpothers.html')


def dashboard(request):
    return render(request, 'dashboard.html')

#LOGIN
def login_page(request):

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        student = Student.objects.filter(

            username=username,
            password=password

        ).first()

        if student:

            request.session['student_id'] = student.id

            request.session['student_name'] = student.username

            return redirect('dashboard')

        else:

            messages.error(

                request,
                "Account not found. Please signup first."
            )

            return redirect('signup')

    return render(request, 'login.html')


# SIGNUP
def signup_page(request):

    if request.method == "POST":

        full_name = request.POST.get('full_name')

        email = request.POST.get('email')

        username = request.POST.get('username')

        password = request.POST.get('password')

        student = Student.objects.filter(username=username).first()

        if student:

            messages.error(request, "Username already exists")

            return redirect('signup')

        Student.objects.create(

            full_name=full_name,
            email=email,
            username=username,
            password=password
        )

        messages.success(request, "Account created successfully")

        return redirect('login')

    return render(request, 'signup.html')