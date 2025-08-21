from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'mpesa'

urlpatterns = [
    path('initiate/<int:bill_id>/', views.initiate_stk_push, name='initiate_payment'),
    path('callback/', csrf_exempt(views.mpesa_callback), name='callback'),
]
