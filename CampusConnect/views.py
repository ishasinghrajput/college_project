from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *  

def home(request):
    return render(request, 'home.html')

def myposts(request):

    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])

    posts = Post.objects.filter(student=student).order_by('-created_at')

    help_requests = HelpRequest.objects.filter(
        post__student=student
    ).select_related('helper', 'post')

    return render(request, 'myposts.html', {
        'student': student,
        'posts': posts,
        'help_requests': help_requests
    })


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


def helpothers(request):

    if 'student_id' not in request.session:
        return redirect('login')

    logged_in_id = request.session['student_id']

    current_student = Student.objects.get(id=logged_in_id)

    posts = Post.objects.all().exclude(student=current_student).order_by('-created_at')

    return render(request, 'helpothers.html', {
        'posts': posts
    })

def dashboard(request):
    if 'student_id' not in request.session:
        return redirect('login')

    current_student = Student.objects.get(id=request.session['student_id'])
    all_posts = Post.objects.exclude(status="RESOLVED").order_by('-created_at')

    for post in all_posts:
        existing_request = HelpRequest.objects.filter(post=post, helper=current_student).first()
        
        if existing_request:
            post.has_requested = True
            post.is_accepted = existing_request.is_accepted
            
            if existing_request.is_accepted:
                active_room = ChatRoom.objects.filter(post=post, helper=current_student).first()
                if active_room:
                    post.active_room_id = active_room.id
        else:
            post.has_requested = False
            post.is_accepted = False

        if post.status == "IN_PROGRESS" and not post.is_accepted:
            post.taken_by_others = True
            accepted_req = HelpRequest.objects.filter(post=post, is_accepted=True).select_related('helper').first()
            if accepted_req:
                post.current_helper_name = accepted_req.helper.username
        else:
            post.taken_by_others = False

    return render(request, 'dashboard.html', {
        'student': current_student,
        'all_posts': all_posts,
    })




def staff_dashboard(request):

    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])

    if student.role != "STAFF":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

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


def post_need(request):
    if 'student_id' not in request.session:
        return redirect('login')
        
    logged_in_id = request.session['student_id']
    current_student = Student.objects.get(id=logged_in_id)
        
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        
        Post.objects.create(
            student=current_student, 
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


def send_help_request(request, post_id):

    if 'student_id' not in request.session:
        return redirect('login')

    helper = Student.objects.get(id=request.session['student_id'])
    post = get_object_or_404(Post, id=post_id)

    if post.student == helper:
        messages.error(request, "You cannot help your own post!")
        return redirect('dashboard')

    already = HelpRequest.objects.filter(post=post, helper=helper).exists()

    if not already:
        HelpRequest.objects.create(post=post, helper=helper)
        messages.success(request, "Request sent!")

    return redirect('dashboard')


 
def logout_view(request):
    request.session.flush() 
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


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

    if 'student_id' not in request.session:
        return redirect('login')

    admin = Student.objects.get(id=request.session['student_id'])

    if admin.role != "ADMIN":
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id)

    if student.role == "USER":
        student.delete()
        messages.success(request, "Student deleted successfully")
    else:
        messages.error(request, "You cannot delete this user")


def about_platform(request):
    return render(request, 'about.html')



def accept_chat_request(request, request_id):
    if 'student_id' not in request.session:
        return redirect('login')

    owner = Student.objects.get(id=request.session['student_id'])
    help_request = get_object_or_404(HelpRequest, id=request_id)

    if help_request.post.student != owner:
        messages.error(request, "Unauthorized access!")
        return redirect('dashboard')

    help_request.is_accepted = True
    help_request.save()

    main_post = help_request.post
    main_post.status = "IN_PROGRESS"
    main_post.save()  

    room, created = ChatRoom.objects.get_or_create(
        post=main_post,
        requester=main_post.student,
        helper=help_request.helper
    )

    return redirect('chatroom', room_id=room.id)



def reopen_post(request, post_id):
    if 'student_id' not in request.session:
        return redirect('login')

    owner = Student.objects.get(id=request.session['student_id'])
    
    post = get_object_or_404(Post, id=post_id, student=owner)
    
    post.status = "OPEN"
    post.save()

    ChatRoom.objects.filter(post=post).delete()

   
    HelpRequest.objects.filter(post=post, is_accepted=True).delete()
    messages.success(request, "🔄 Post reopened! Previous active chat has been cancelled. You can now accept other pending requests.")
    return redirect('myposts')



def mark_resolved(request, post_id):
    if 'student_id' not in request.session:
        return redirect('login')

    owner = Student.objects.get(id=request.session['student_id'])
    post = get_object_or_404(Post, id=post_id, student=owner)

    if post.status == "RESOLVED":
        return redirect('myposts')

    post.status = "RESOLVED"
    post.save()

    accepted_req = HelpRequest.objects.filter(post=post, is_accepted=True).first()

    if accepted_req:
        helper = accepted_req.helper
        points = 10
        helper.points += points
        helper.save()
        messages.success(request, f"🎉 Problem resolved! +{points} points awarded to {helper.username}.")
   
    return redirect('myposts')





def chatroom(request, room_id):

    current_student = Student.objects.get(id=request.session['student_id'])
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.method == "POST":
        if room.post.status == "RESOLVED":
            return redirect('chatroom', room.id)

        msg = request.POST.get('message')

        if msg:
            Message.objects.create(
                room=room,
                sender=current_student,
                message=msg   # IMPORTANT
            )

        return redirect('chatroom', room.id)

    messages = Message.objects.filter(room=room).order_by('timestamp')

    return render(request, "chatroom.html", {
        "room": room,
        "messages": messages,
        "student": current_student
    })


def my_chats(request):
    if 'student_id' not in request.session:
        return redirect('login')

    current_student = Student.objects.get(id=request.session['student_id'])

    requester_chats = ChatRoom.objects.filter(
        requester=current_student
    ).select_related('post', 'helper').order_by('-created_at')

    helper_chats = ChatRoom.objects.filter(
        helper=current_student
    ).select_related('post', 'requester').order_by('-created_at')

    context = {
        'student': current_student,
        'requester_chats': requester_chats,
        'helper_chats': helper_chats
    }

    return render(request, 'my_chats.html', context)




