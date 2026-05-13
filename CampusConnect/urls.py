from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('myposts/', views.myposts, name='myposts'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('hellpothers/', views.helpothers, name='helpothers'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
]

