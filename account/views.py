from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


def signup_view(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse('done')
        else:
            return HttpResponse('No1')
    else:
        return HttpResponse('No')
