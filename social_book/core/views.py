from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from .models import Profile
from django.http import HttpResponse
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')

# Create your views here

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create(username=username, email=email, password=make_password(password))
                user.save()


                # log user in and redirect to settings pageY

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
            
                #create profile object for the new user
                user_model  = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user = user_model.id)
                new_profile.save()

                return redirect('settings')
        else:
            messages.info(request,'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    print(user_profile)
    # return render(request,'setting.html')

    return render(request, 'setting.html',{'user_profile':user_profile})