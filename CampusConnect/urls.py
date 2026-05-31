from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_platform, name='about_platform'),
    path('myposts/', views.myposts, name='myposts'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff-dashboard/',views.staff_dashboard,name='staff_dashboard'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('hellpothers/', views.helpothers, name='helpothers'),   
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('post-need/', views.post_need, name='post_need'),
    path('resolve/<int:post_id>/', views.mark_resolved, name='mark_resolved'),
    path('accept/<int:request_id>/', views.accept_chat_request, name='accept_chat_request'),
    path('chat/<int:room_id>/', views.chatroom, name='chatroom'),
    path('my-chats/', views.my_chats, name='my_chats'),
    path('reopen-post/<int:post_id>/', views.reopen_post, name='reopen_post'),
    path('send-help-request/<int:post_id>/', views.send_help_request, name='send_help_request'),
    path('logout/', views.logout_view, name='logout'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('staff-list/', views.staff_list, name='staff_list'),
    path('manage-posts/', views.manage_posts, name='manage_posts'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete-student/<int:student_id>/',views.delete_student,name='delete_student'),
]
