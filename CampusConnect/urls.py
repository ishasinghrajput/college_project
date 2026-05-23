from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('myposts/', views.myposts, name='myposts'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff-dashboard/',views.staff_dashboard,name='staff_dashboard'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('hellpothers/', views.helpothers, name='helpothers'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('development-team/',views.development_team, name= 'development_team'),
    # === Jaroori Paths Jo Add Kiye Hain ===
    
    # 1. Naya Post (Need Form) open karne aur save karne ke liye
    path('post-need/', views.post_need, name='post_need'),
    
    # 2. Help Now button click hone par request bhejne ke liye (Post ID ke saath)
    path('send-help-request/<int:post_id>/', views.send_help_request, name='send_help_request'),
    
    # 3. Securely logout karne ke liye
    path('logout/', views.logout_view, name='logout'),

    path('manage-students/', views.manage_students, name='manage_students'),

    path('staff-list/', views.staff_list, name='staff_list'),

    path('manage-posts/', views.manage_posts, name='manage_posts'),

    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path(
        'delete-student/<int:student_id>/',
        views.delete_student,
        name='delete_student'
    ),
]
