from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from uks_app.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from uks_app.models import ObservedProject, User


# user registration 
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are able to log in now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, "uks_app/register.html", {'form' : form})

# user profile
def profile(request, id=None):
    selected_user = get_object_or_404(User, username=id)
    selected_user_following = selected_user.profile.following.all() # users that the selected user is following    
    selected_user_followers = selected_user.profile.followers.all() # users that the selected user is followed by
    my_following = [] # users that the logged in user is following
    final_for_followers = []
    final_for_following = []
    if request.user.is_authenticated: # if the user is logged in
        my_following = request.user.profile.following.all() 
        for i in selected_user_following: 
            if i.user.profile in my_following:      # if the user is followed by the logged in user, it can be unfollowed    
                final_for_following.append(False)
            if i.user.profile not in my_following:  # if the user is not followed by the logged in user, it can be followed
                final_for_following.append(True)
            if i.user == request.user:      # if it is a logged in user it can neither be unfollowed nor followed
                final_for_following.append(False)
        for i in selected_user_followers:
            if i.user.profile in my_following:      # if the user is followed by the logged in user, it can be unfollowed 
                final_for_followers.append(False)
            if i.user.profile not in my_following:  # if the user is not followed by the logged in user, it can be followed
                final_for_followers.append(True) 
            if i.user == request.user:              # if it is a logged in user it can neither be unfollowed nor followed
                final_for_followers.append(False)

    project_colab = []
    if selected_user == request.user:
        project_colab = selected_user.collaborators.all()
        projects = ObservedProject.objects.filter(user=selected_user)
    elif request.user.is_authenticated:
        my_collaborations = request.user.collaborators.all()
        projects = ObservedProject.objects.filter(user=selected_user).exclude(Q(public=False) & ~Q(id__in=my_collaborations))
    else:
        projects = ObservedProject.objects.filter(user=selected_user).exclude(public=False)

    update_possible = selected_user == request.user
    follow_possible = selected_user != request.user and selected_user.profile not in my_following and request.user.is_authenticated
    unfollow_possible =  selected_user != request.user and selected_user.profile in my_following and request.user.is_authenticated
    context = {
        'selected_user': selected_user,
        'projects' : projects,
        'update_possible' : update_possible,
        'selected_user_following' : selected_user_following,
        'selected_user_followers' : selected_user_followers,
        'follow_possible': follow_possible,
        'unfollow_possible': unfollow_possible,
        'final_for_following': final_for_following,
        'final_for_followers': final_for_followers,
        'project_colab' : project_colab
    }
    return render(request, 'uks_app/profile.html', context)

# user profile update
@login_required
def profile_update(request, id=None):
    selected_user = get_object_or_404(User, username=id)

    if request.user != selected_user:
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=selected_user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=selected_user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile', selected_user.username)
    else:
        u_form = UserUpdateForm(instance=selected_user)
        p_form = ProfileUpdateForm(instance=selected_user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'uks_app/profile_update.html', context)



@login_required
def search_collaborators(request, project_id):
    
    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)
    if request.user == observed_project.user:
        if request.method == 'POST':
            search_name = request.POST['search']
            result = User.objects.filter(Q(first_name__icontains = search_name.lower()) | Q(last_name__icontains = search_name.lower()) | Q(username__icontains = search_name.lower()) & Q(is_staff='False')).exclude(username=observed_project.user.username).exclude(id__in=[user.id for user in observed_project.collaborators.all()]).distinct()
        else:
            result = []

        context = {
            "observed_project": observed_project,
            "result": result,
        }

        return render(request, 'uks_app/add_collaborators.html', context)   

@login_required
def add_collaborators(request, project_id, user_id):
    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)
    if request.user == observed_project.user:
        #get user
        user = get_object_or_404(User, id=user_id)
        observed_project.collaborators.add(user)
        return HttpResponseRedirect('/project/' + str(project_id) + '/')

    return HttpResponse('Unauthorized', status=401)

@login_required
def remove_collaborators(request, project_id, user_id):
    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)
    if request.user == observed_project.user:
        #get user
        user = get_object_or_404(User, id=user_id)
        observed_project.collaborators.remove(user)
        return HttpResponseRedirect('/project/' + str(project_id) + '/')
    
    return HttpResponse('Unauthorized', status=401)