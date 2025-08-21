from django.contrib import admin
from django.urls import path, include, reverse
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Redirect for incorrect admin register user URL
    path('admin/register_user/', lambda request: redirect(reverse('account:admin_register_user'))),
    
    # Main app URLs
    path('admin/', admin.site.urls),
    path('account/', include('account.urls', namespace='account')),  # All account URLs under /account/
    path('', include('main.urls', namespace='main')),
    path('mpesa/', include('mpesa.urls')),
    
    # Auth URLs (for password reset)
    path('password_reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='account/password_reset.html',
            email_template_name='account/password_reset_email.html',
            subject_template_name='account/password_reset_subject.txt',
            success_url='/password_reset/done/'
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
            success_url='/reset/done/'
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
