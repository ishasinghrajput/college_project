from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Post  # Post table import kar li hai

# Create your views here.

def home(request):
    return render(request, 'home.html')


def myposts(request):
    if 'student_id' not in request.session:
        return redirect('login')
        
    logged_in_id = request.session['student_id']
    current_student = Student.objects.get(id=logged_in_id)
    context = {
        'student': current_student,
    }
    
    return render(request, 'myposts.html', context)


def profile(request):
    return render(request, "profile.html")  # Changed to load standard .html template


def helpothers(request):
    return render(request, 'helpothers.html')


# LOGGED IN USER DASHBOARD (FETCHES ALL CAMPUS POSTS)
def dashboard(request):
    if 'student_id' not in request.session:
        return redirect('login')
        
    logged_in_id = request.session['student_id']
    current_student = Student.objects.get(id=logged_in_id)
    
    # Database se saare posts fetch karke dashboard par bhejne ke liye (Newest First)
    all_posts = Post.objects.all().order_by('-created_at')
    
    context = {
        'student': current_student,
        'all_posts': all_posts  # Template loop ke liye data pass kiya
    }
    
    return render(request, 'dashboard.html', context)



# POST A NEED FORM INTERFACE (SAVES NEW REQUEST)
def post_need(request):
    if 'student_id' not in request.session:
        return redirect('login')
        
    # Active logged-in student ka object nikalna taaki navbar login state me rahe
    logged_in_id = request.session['student_id']
    current_student = Student.objects.get(id=logged_in_id)
        
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        
        # Table me data save karna
        Post.objects.create(
            student=current_student, # Directly passing student object
            title=title,
            category=category,
            description=description
        )
        
        messages.success(request, "Your help request has been posted successfully!")
        return redirect('dashboard')
        
    context = {
        'student': current_student
    }
    return render(request, 'postneed.html', context)



# HELP NOW CLICK ACTIVITY ACTION HANDLER
def send_help_request(request, post_id):
    if 'student_id' not in request.session:
        return redirect('login')
        
    helper_id = request.session['student_id']
    post_obj = get_object_or_400(Post, id=post_id)
    
    # Check: Student khud ke hi post par help click na kare
    if post_obj.student.id == helper_id:
        messages.error(request, "You cannot send a help request to your own post!")
        return redirect('dashboard')
        
    # Notification push execution message
    messages.success(request, f"Help request notification sent to {post_obj.student.username} successfully!")
    return redirect('dashboard')


# LOGOUT CONTROLLER
def logout_view(request):
    request.session.flush()  # Clear sessions data securely
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# LOGIN PROCESS
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
            messages.success(request, "Welcome  Ready to connect and help others?")
            return redirect('dashboard')
        else:
            messages.error(
                request,
                "Account not found. Please signup first."
            )
            return redirect('signup')

    return render(request, 'login.html')


# SIGNUP PROCESS
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



