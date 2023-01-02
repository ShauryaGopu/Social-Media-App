from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount
# Register your models here.
# Here I adding my first model named Profile
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
