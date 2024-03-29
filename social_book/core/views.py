from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from .models import Profile, Post, LikePost, FollowersCount
from django.http import HttpResponse
from django.contrib import messages
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
import random

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    followings = FollowersCount.objects.filter(follower=request.user.username)
    
    for following in followings:
        user_following_list.append(following.user)
    for usernam in user_following_list:
        feed.append(Post.objects.filter(user=usernam))

    posts = list(chain(*feed))
    
    #profiles = Profile.objects.exclude(user = user_object)

    #user suggestion starts here
    all_users = User.objects.all()
    user_following_all = []
    for user in followings:
        user_list = User.objects.get(username=user)
        user_following_all.append(user_list)

    suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]

    current_user = User.objects.filter(username=request.user.username)

    final_suggestions = [x for x in list(suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions)

    username_profile  = []
    profiles = []
    
    for user in final_suggestions:
        username_profile.append(user.id)

    for id in username_profile:
        profile_lists = Profile.objects.filter(id_user = id)
        profiles.append(profile_lists)
    
    profiles = list(chain(*profiles))

    return render(request, 'index.html',{'user_profile':user_profile, 'posts':posts , 'profiles':profiles[:4]})

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
def search(request):

    user_object =  User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)
        for id in username_profile:
            username_profile_list.append(Profile.objects.filter(id_user=id))
        
        username_profile_list = list(chain(*username_profile_list))

        return render(request, 'search.html',{'user_profile':user_profile, 'username_profile_list':username_profile_list})
    

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



@login_required(login_url='signin')
def profile(request,pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower = follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'


    user_followers = len(FollowersCount.objects.filter(user=pk))
    users_following = len(FollowersCount.objects.filter(follower=pk))
    context = {
        'user_object' : user_object,
        'user_profile' : user_profile,
        'user_posts':user_posts,
        'user_posts_length':user_posts_length,
        'button_text':button_text,
        'user_followers' : user_followers,
        'users_following' : users_following
    }

    return render(request, 'profile.html',context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        if FollowersCount.objects.filter(follower = follower, user = user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user = user)
            delete_follower.delete()
        else:
            new_follower = FollowersCount.objects.create(follower = follower, user = user)
            new_follower.save()
        
        return redirect('/profile/'+user)
    else:
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