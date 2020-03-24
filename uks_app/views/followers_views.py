from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from uks_app.models import User

@login_required
@api_view(['POST', ])
def follow(request):
    user = request.user # ulogovani korisnik
    if request.method == 'POST':
        selected_user = get_object_or_404(User, username=request.data['username']) # onaj kojeg zelim da zapratim
        user.profile.following.add(selected_user.profile)   
        selected_user.profile.followers.add(user.profile)
    return HttpResponse('Followed', status=200)

@login_required
@api_view(['POST', ])
def unfollow(request):
    user = request.user # ulogovani korisnik
    if request.method == 'POST':
        selected_user = get_object_or_404(User, username=request.data['username']) # onaj kojeg zelim da otpratim
        user.profile.following.remove(selected_user.profile)   
        selected_user.profile.followers.remove(user.profile)
    return HttpResponse('Unfollowed', status=200)