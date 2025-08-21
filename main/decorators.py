from functools import wraps
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from main.models import *
import sweetify


def verified_or_superuser(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        profile = request.user
        if profile.verified or profile.is_superuser:
             return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('account:login'))

  return wrap

def client_facing_login_required(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            sweetify.error(request, 'You must be logged in to view this page.', button='Login')
            return redirect('landingpage')
  return wrap





