from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'users'

urlpatterns = [
    # User register: reverse(users:register) == '/register/'  # Used for redirect: namespace(url):name(child app url)
    path('register/', views.RegisterView.as_view(), name='register'),
    # Check whether username registered repeatedly
    url(r'^usernames/(?P<username>[a-zA-Z0-9-_]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobile/(?P<mobile>\d{10})/count/$', views.MobileCountView.as_view()),
    # User login
    path('login/', views.LoginView.as_view(), name='login'),
    # User logout
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # User center info
    path('info/', views.UserInfoView.as_view(), name='info'),
]