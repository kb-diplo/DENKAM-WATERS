from django.urls import path
from .views import (
    login_view, 
    logout_view, 
    RegisterView, 
    profile_view, 
    dashboard_view
)

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
]