from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from .models import Profile, Post, LikePost
from django.http import HttpResponse
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    posts = Post.objects.all()

    return render(request, 'index.html',{'user_profile':user_profile, 'posts':posts})

# Create your views here
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if not like_filter :
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect('/')
    
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('/')










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
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')

        bio =  request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg =image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()    
        
        return redirect('settings')

    #print(user_profile)
    # return render(request,'setting.html')
    return render(request, 'setting.html',{'user_profile':user_profile})