from django.shortcuts import render, redirect
from login.forms import RegistrationForm, EditProfileForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from login import models
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


def home(request):
    return render(request, 'login/home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('..')
            # return render(request, 'rsvp/home.html',{})
            # HttpResponseRedirect('/rsvp/')
        else:
            form = RegistrationForm()
            args = {'form': form}
            return render(request, 'login/reg_form.html', args)
    else:
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'login/reg_form.html', args)


# @login_required


def profile(request):
    args = {'user': request.user}
    return render(request, 'login/profile.html', args)


# @login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('../profile')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'login/edit_profile.html', args)


# @login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('../profile')
        else:
            return redirect('../change-password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'login/change_password.html', args)



# Create your views here.
