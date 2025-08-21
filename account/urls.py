from django.urls import path
from . import views
from .views import (
    meter_reader_register_user_view,
    admin_register_user_view,
    admin_register_meter_reader_view,
    meter_reader_dashboard,
    login_view,
    logout_view,
    landingpage
)
from django.contrib.auth import views as auth_views

app_name = 'account'

urlpatterns = [
    # Public URLs
    path('', landingpage, name="landingpage"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    
    # Admin URLs
    path('admin/register/user/', admin_register_user_view, name='admin_register_user'),
    path('register/meter-reader/', admin_register_meter_reader_view, name='admin_register_meter_reader'),
    
    # Meter Reader URLs
    path('meter-reader/register-client/', meter_reader_register_user_view, name='meter_reader_register_user'),
    path('dashboard/meter-reader/', meter_reader_dashboard, name='meter_reader_dashboard'),
    

    # Password reset
    path('password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='account/password_reset.html',
            email_template_name='account/password_reset_email.html',
            subject_template_name='account/password_reset_subject.txt',
            success_url='done/'
        ),
        name='password_reset'
    ),
    path('password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='account/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='account/password_reset_confirm.html',
            success_url='/account/reset/done/'
        ),
        name='password_reset_confirm'
    ),
    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='account/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
