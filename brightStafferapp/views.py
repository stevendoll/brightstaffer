from brightStafferapp.form import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
#from brightStafferapp.models import signup
from django.contrib.auth import logout

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            user.is_active = True
            user.first_name=form.cleaned_data['first_name']
            user.last_name=form.cleaned_data['last_name']
            user.password2 = form.cleaned_data['password2']
            user.set_password(user.password2)
            return HttpResponseRedirect('/login/')
    else:
        form = RegistrationForm()
    context={
    'form': form,
    }

    return render(request,'registration/register.html', context)


@csrf_protect
def login(request):
    template_name="registration/login.html"
    context={}
    if request.method=="POST":
        username=request.POST['UserName']
        if username=='':
            message="UserName can't be blank"
            context = {'message': message}
            return render(request, template_name, context)
        password=request.POST['Password']
        if password=='':
            message="Password can't be blank"
            context = {'message': message}
            return render(request, template_name, context)
        user = User.objects.all().values_list('username', 'password', 'email').filter(username=username)
        if user.count() and check_password(password, user[0][1]):
            request.session['is_logged_in'] = True
            request.session['username'] = username
            return redirect('/dashboard/')
        else:
            message="Username and Password didn't match"
        context = {'message': message}
        return render(request, template_name, context)
    return render(request, template_name, context)



def dashboard(request):
    template_name="Dashboard.html"
    context={}
    return render(request, template_name, context)


def user_logout(request):
    logout(request)
    return redirect('/login/')
