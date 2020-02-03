from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ObservedProject, Issue
from .forms import ProjectForm, IssueForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import logging

# home page
def index(request):
    return render(request, 'uks_app/index.html') #optional third argument context

# new project form
def create_update_project(request, project_id=None):

    #project_id == None -> Create
    #project_id != None -> Update
    observed_project = get_object_or_404(ObservedProject, pk=project_id) if project_id else None

    form = ProjectForm(request.POST or None, instance=observed_project)

    if form.is_valid():
        form.save()
        
        if project_id:
            return HttpResponseRedirect('/project/' + str(project_id) + '/')  
        else:
            return HttpResponseRedirect('/project/')

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_update_project.html', context)

# new issue form
def create_update_issue(request, project_id, issue_id=None):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    #issue_id == None -> Create
    #issue_id != None -> Update
    observed_issue = get_object_or_404(Issue, pk=issue_id) if issue_id else None

    form = IssueForm(request.POST or None, instance=observed_issue)

    if form.is_valid():
        issue = form.save(commit=False)
        
        #set project as foreign key
        issue.project = observed_project
        issue.save()
        
        if issue_id:
            return HttpResponseRedirect('/project/' + str(project_id) + '/issue/' + str(issue_id) + '/')  
        else:
            return HttpResponseRedirect('/project/' + str(project_id) + '/issue/' + str(issue.id) + '/')  

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_update_issue.html', context)

#change issue state
def change_issue_state(request, project_id, issue_id):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)
    
    #get issue
    observed_issue = get_object_or_404(Issue, id=issue_id)

    if observed_issue.state == "OP":
        observed_issue.state = "CL"
    else:
        observed_issue.state = "OP"
    
    observed_issue.save()

    return HttpResponseRedirect('/project/' + str(project_id) + '/issue/' + str(issue_id) + '/')

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
    projects = ObservedProject.objects.filter(user=selected_user)
    update_possible = selected_user == request.user
    print(update_possible)
    context = {"selected_user": selected_user, 'projects' : projects, 'update_possible' : update_possible}
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


#delete project
class ProjectDelete(DeleteView):
    template_name = 'uks_app/delete_project.html'
    model = ObservedProject

    success_url = reverse_lazy('all_projects')

#delete project
class IssueDelete(DeleteView):
    template_name = 'uks_app/delete_issue.html'
    model = Issue

    success_url = reverse_lazy('all_projects')

# all projects view
class ProjectView(generic.ListView):
    template_name = 'uks_app/all_projects.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return ObservedProject.objects.all()

# one project detailed view
class OneProjectView(generic.DetailView):
    model = ObservedProject
    template_name = 'uks_app/one_project.html'

# one issue detailed view
class OneIssueView(generic.DetailView):
    model = Issue
    template_name = 'uks_app/one_issue.html'