from django.shortcuts import render
from django.http import HttpResponse



def index(request):
    return render(request, 'index.html')

# Create your views here.

def signup(request):

    if request.method == 'POST':
        username = request.POST('username')
        email = request.POST('email')
        password = request.POST('password')
        print(username, email, password)
    else:
        return render(request, 'signup.html')