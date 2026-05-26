from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Post  # Post table import kar li hai


# HOME PAGE
def home(request):
    return render(request, 'home.html')


# MY POSTS PAGE
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

#HELPOTHERS
def helpothers(request):

    if 'student_id' not in request.session:
        return redirect('login')

    logged_in_id = request.session['student_id']

    current_student = Student.objects.get(id=logged_in_id)

    # FIXED QUERY
    posts = Post.objects.all().exclude(student=current_student).order_by('-created_at')

    return render(request, 'helpothers.html', {
        'posts': posts
    })

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


def staff_dashboard(request):

    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])

    if student.role != "STAFF":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    #THIS IS MISSING (MAIN FIX)
    posts = Post.objects.all().order_by('-created_at')

    return render(request, 'staff_dashboard.html', {
        'student': student,
        'posts': posts
    })


def admin_dashboard(request):

    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])

    if student.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    posts = Post.objects.all().order_by('-created_at')

    total_students = Student.objects.filter(role="USER").count()
    total_staff = Student.objects.filter(role="STAFF").count()
    total_posts = Post.objects.count()

    return render(request, 'admin_dashboard.html', {
        'student': student,
        'posts': posts,
        'total_students': total_students,
        'total_staff': total_staff,
        'total_posts': total_posts
    })


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
    post_obj = get_object_or_404(Post, id=post_id)
    
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
        role = request.POST.get('role')

        student = Student.objects.filter(
            username=username,
            password=password,
            role=role
        ).first()

        if student:

            request.session['student_id'] = student.id

            request.session['student_name'] = student.username

            request.session['role'] = student.role

            

            # ROLE BASED REDIRECT

            if student.role == "USER":
                messages.success(request,"Welcome Ready to connect and help others?")
                return redirect('dashboard')


            elif student.role == "STAFF":
                return redirect('staff_dashboard')

            elif student.role == "ADMIN":
                return redirect('admin_dashboard')
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
        role = request.POST.get('role')

        student = Student.objects.filter(username=username).first()

        if student:
            messages.error(request, "Username already exists")
            return redirect('signup')

        Student.objects.create(
            full_name=full_name,
            email=email,
            username=username,
            password=password,
            role=role
        )
        

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'signup.html')



def manage_students(request):

    if 'student_id' not in request.session:
        return redirect('login')

    admin = Student.objects.get(id=request.session['student_id'])

    if admin.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    students = Student.objects.filter(role="USER")

    return render(request, 'manage_students.html', {
        'students': students
    })

def staff_list(request):

    if 'student_id' not in request.session:
        return redirect('login')

    admin = Student.objects.get(id=request.session['student_id'])

    if admin.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    staffs = Student.objects.filter(role="STAFF")

    return render(request, 'staff_list.html', {
        'staffs': staffs
    })

def manage_posts(request):

    if 'student_id' not in request.session:
        return redirect('login')

    admin = Student.objects.get(id=request.session['student_id'])

    if admin.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    posts = Post.objects.all().order_by('-created_at')

    return render(request, 'manage_posts.html', {
        'posts': posts
    })

def delete_post(request, post_id):

    if 'student_id' not in request.session:
        return redirect('login')

    admin = Student.objects.get(id=request.session['student_id'])

    if admin.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    post = get_object_or_404(Post, id=post_id)
    post.delete()

    return redirect('admin_dashboard')

def delete_student(request, student_id):

    # login check
    if 'student_id' not in request.session:
        return redirect('login')

    admin = Student.objects.get(id=request.session['student_id'])

    # only admin allowed
    if admin.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id)

    # safety: admin or staff delete nahi hoga (optional safeguard)
    if student.role == "USER":
        student.delete()
        messages.success(request, "Student deleted successfully")
    else:
        messages.error(request, "You cannot delete this user")
