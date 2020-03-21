from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from uks_app.models import ObservedProject, User, Issue

#search projects from name
def search_projects(request):
    search_name = request.GET['search']
    observed_projects = ObservedProject.objects.filter(name__icontains=search_name.lower()).filter(public = 'True')
    issues_list =Issue.objects.filter(title__icontains=search_name.lower(), project__public='True')
    users_list=User.objects.filter(Q(first_name__icontains = search_name.lower()) | Q(last_name__icontains = search_name.lower()) | Q(username__icontains = search_name.lower()) & Q(is_staff='False'))
    user = request.user # logged in user
    follow_possible = []
    if user.is_authenticated: # if the user is logged in
        users_following = user.profile.following.all() # users that the logged in user is following
        for user in users_list:                        
            if user.profile in users_following: # already follows, so he can only unfollow him
                follow_possible.append(False) 
            else:
                follow_possible.append(True)    # he doesn't follow him, so he can follow him
    return render(request, 'uks_app/search_result.html', {'observed_projects': observed_projects, 'issues_list':issues_list, 'users_list':users_list, 'follow_possible': follow_possible, 'request_user': user})
