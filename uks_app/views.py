from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from .models import ObservedProject, Issue, Milestone, MilestoneChange, Event, Label, User, Comment, CommentChange, CodeChangeEvent, AssignIssueEvent, IssueChange
from .forms import ProjectForm, IssueForm, MilestoneForm, LabelForm, ChooseLabelForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ChooseMilestoneForm, CommentForm, ChooseSubissueForm, AssignIssueForm
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ObservedProject, Issue, CodeChange
from .forms import ProjectForm, IssueForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import datetime
import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# home page
def index(request): 
    return render(request, 'uks_app/index.html') #optional third argument context

# new project form
@login_required
def create_update_project(request, project_id=None):
 
    user = request.user

    #project_id == None -> Create
    #project_id != None -> Update
    observed_project = get_object_or_404(ObservedProject, pk=project_id) if project_id else None

    # only project owner can make changes to the project
    if project_id != None and observed_project.user != request.user:
        return HttpResponse('Unauthorized', status=401)

    form = ProjectForm(request.POST or None, instance=observed_project)

    if form.is_valid():
         
        project = form.save(commit=False) 
 
        project.user = user
        project.save()

        if project_id:
            return HttpResponseRedirect('/project/' + str(project_id) + '/')  
        else:
            return HttpResponseRedirect('/project/')

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_update_project.html', context)

# new issue form
@login_required
def create_update_issue(request, project_id, issue_id=None):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    #issue_id == None -> Create
    #issue_id != None -> Update
    observed_issue = get_object_or_404(Issue, pk=issue_id) if issue_id else None

    # only project owner and collaborators can create a public issue
    if issue_id == None and observed_project.public == False and request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    # only project owner and collaborators can update a issue
    if issue_id != None and request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)

    form = IssueForm(data=request.POST or None, project=observed_project, iss=observed_issue, instance=observed_issue)

    if form.is_valid():
        issue = form.save(commit=False)
       
        if not issue_id:
            issue.create_time = datetime.datetime.now()
        
        #set project as foreign key
        issue.project = observed_project
        issue.save()
        
        if issue_id:
            return HttpResponseRedirect('/issue/' + str(issue_id) + '/')  
        else:
            return HttpResponseRedirect('/issue/' + str(issue.id) + '/')  

    cancel_url = "../../../../../issue/"+str(issue_id) if issue_id else "../../"

    
    context = {
        'form' : form,
        'cancel_url': cancel_url
    }

    return render(request, 'uks_app/create_update_issue.html', context)

# new label form
@login_required
def create_label(request, issue_id):

    #get issue
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    # only project owner and collaborators can create a new label
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    form = LabelForm(request.POST or None)

    if form.is_valid():
        label = form.save(commit=True)
        
        #set issue as foreign key
        label.issue.add(observed_issue)
        label.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_label.html', context)
    

# choose label
@login_required
def choose_label(request, issue_id):

    #get issue and project
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    # only project owner and collaborators can choose a label
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    project_issues = observed_project.issue_set.exclude(id=issue_id)

    form = ChooseLabelForm(project_issues, observed_issue, data=request.POST or None)

    if form.is_valid():
        chosen_labels = form.cleaned_data['labels']
        
        for label in chosen_labels:
            label.issue.add(observed_issue)
            label.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
        'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_label.html', context)

@login_required
def choose_subissue(request, issue_id):

    #get issue 
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    # only project owner and collaborators can choose a subissue
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)

    form = ChooseSubissueForm(observed_issue, data=request.POST or None)

    if form.is_valid():
    
        chosen_issues = form.cleaned_data['issues']
        
        for issue in chosen_issues:
            if issue.parent_issue == None and issue != observed_issue:
                issue.parent_issue = observed_issue

                issue.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
        'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_subissue.html', context)

@login_required
def remove_subissue(request, issue_id, subissue_id):

    #get issue
    issue = get_object_or_404(Issue, id=issue_id)
    observed_project = issue.project

    # only project owner and collaborators can remove a subissue
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)

    #get subissue
    subissue = get_object_or_404(Issue, id=subissue_id)

    issue.subissues.remove(subissue)

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

# new subissue form
@login_required
def create_subissue(request, issue_id):

    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    # only project owner and collaborators can create a subissue
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)

    form = IssueForm(data=request.POST or None, project=observed_project, iss=observed_issue)

    if form.is_valid():
        issue = form.save(commit=False)
        
        #set project as foreign key
        issue.project = observed_project

        #set parent issue
        issue.parent_issue = observed_issue

        issue.create_time = datetime.datetime.now()

        issue.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')  
    
    context = {
        'form' : form,
        'cancel_url': "../"
    }

    return render(request, 'uks_app/create_update_issue.html', context)

#change issue state
def change_issue_state(request, project_id, issue_id):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    # only project owner and collaborators can change issue state
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    #get issue
    observed_issue = get_object_or_404(Issue, id=issue_id)

    if observed_issue.state == "OP":
        observed_issue.state = "CL"
        q = IssueChange.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, state="CL")

    else:
        observed_issue.state = "OP"
        q = IssueChange.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, state="OP")
    
    observed_issue.save()

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

# assign issue
@login_required
def assign_issue(request, issue_id):

    #get issue and project
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project
    
    # only project owner and collaborators can assign a issue
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    form = AssignIssueForm(observed_issue, data=request.POST or None)

    if form.is_valid():
        
        chosen_user = form.cleaned_data['user'].first()
        observed_issue.user=chosen_user
        observed_issue.save()

        assign_issue_event = AssignIssueEvent.objects.create(assigned_user=chosen_user, issue=observed_issue, time=datetime.datetime.now(), user=request.user)

        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
        'issue' : observed_issue
    }

    return render(request, 'uks_app/assign_issue.html', context)

@login_required
def remove_label(request, label_id, issue_id):

    #get issue
    issue = get_object_or_404(Issue, id=issue_id)
    observed_project = issue.project

    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    #get label
    label = get_object_or_404(Label, id=label_id)

    issue.labels.remove(label)

    if label.issue.count() <= 0:
        label.delete()

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

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
            print('? ',  i.user == request.user)
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

    projects = ObservedProject.objects.filter(user=selected_user)
    update_possible = selected_user == request.user
    follow_possible = selected_user != request.user and selected_user.profile not in my_following and request.user.is_authenticated
    unfollow_possible =  selected_user != request.user and selected_user.profile in my_following and request.user.is_authenticated
    context = {"selected_user": selected_user, 'projects' : projects, 'update_possible' : update_possible, "selected_user_following" : selected_user_following, "selected_user_followers" : selected_user_followers, "follow_possible": follow_possible, "unfollow_possible": unfollow_possible, "final_for_following": final_for_following, "final_for_followers": final_for_followers, "request_user" : request.user, }
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

#change code
@require_http_methods(["POST"])
@csrf_exempt
def hook_receiver_view(request):
    request_body_string = request.body.decode("utf-8")
    data = json.loads(request_body_string)
    commit_url=""
    repository_url=""
    message=""
    try:
        commits=data["commits"]
        repository_url=data["repository"]["html_url"]
        project= ObservedProject.objects.filter(git_repo = repository_url)
        if len(project)!=0 :
            for commit in commits:
                commit_url=commit["url"]
                message=commit["message"]
                email=commit["author"]["email"]
                username=commit["author"]["name"]
                time=commit["timestamp"]
                users=User.objects.filter(Q(email = email))
                if len(users)==0:
                    q = CodeChange.objects.create(url=commit_url, project=project.first(), message=message, date_time=time, github_username=username)
                else:
                    q = CodeChange.objects.create(url=commit_url, project=project.first(), message=message, user=users[0], date_time=time, github_username=username)
                
                #povezivanje sa issuima
                regex_matches = re.findall('~(.+?)~', message)
                regex_matches_close = re.findall('close ~(.+?)~', message)
                
                if len(regex_matches_close)!=0 :
                    for match in regex_matches_close:
                        issue= Issue.objects.filter(Q(title = match) & Q(project = project.first()))                        
                        if len(issue) != 0:
                            related_issue=issue.first()
                            related_issue.state='CL'
                            related_issue.save()
                            if len(users)!=0:
                                code_change_event = CodeChangeEvent.objects.create(code_change=q, issue=issue[0], time=time, user=users[0], closing_event=True)
                            else:
                                code_change_event = CodeChangeEvent.objects.create(code_change=q, issue=issue[0], time=time, closing_event=True)
            
                if len(regex_matches)!=0 :
                    for match in regex_matches:
                        if match not in regex_matches_close:
                            issue= Issue.objects.filter(Q(title = match) & Q(project = project.first()))
                            if len(issue) != 0:
                                if len(users)!=0:
                                    code_change_event = CodeChangeEvent.objects.create(code_change=q, issue=issue[0], time=time, user=users[0], closing_event=False)
                                else:
                                    code_change_event = CodeChangeEvent.objects.create(code_change=q, issue=issue[0], time=time, closing_event=False)
            return HttpResponse('success')
        else:
            return HttpResponse('Project does not exist', status=400)

    except Exception as e:
        return HttpResponse('Data is not valid', status=400)

#delete project
class ProjectDelete(DeleteView):
    template_name = 'uks_app/delete_project.html'
    model = ObservedProject

    def dispatch(self, request, *args, **kwargs):
       entity = get_object_or_404(ObservedProject, pk=kwargs['pk'])
       user = request.user

       if user != entity.user:
           return HttpResponse('Unauthorized', status=401)
       return super(ProjectDelete, self).dispatch(request, *args, **kwargs)

    success_url = reverse_lazy('all_projects')

#delete issue
class IssueDelete(DeleteView):
    template_name = 'uks_app/delete_issue.html'
    model = Issue

    def dispatch(self, request, *args, **kwargs):
       entity = get_object_or_404(Issue, pk=kwargs['pk'])
       user = request.user
       observed_project = entity.project

       if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
           return HttpResponse('Unauthorized', status=401)
       return super(IssueDelete, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        project = self.object.project
        return reverse_lazy( 'one_project', kwargs={'pk': project.id})

# all projects view
class ProjectView(generic.ListView):
    template_name = 'uks_app/all_projects.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return ObservedProject.objects.filter(public=True).all()

# one project detailed view
class OneProjectView(generic.DetailView):
    model = ObservedProject
    template_name = 'uks_app/one_project.html'

# one issue detailed view
class OneIssueView(generic.DetailView):
    model = Issue
    template_name = 'uks_app/one_issue.html'

    def get_context_data(self, **kwargs):
        context = super(OneIssueView, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(issue_id=self.kwargs.get('pk')).order_by('time')

        return context

# one milestone detailed view
class OneMilestoneView(generic.DetailView):
    model = Milestone
    template_name = 'uks_app/one_milestone.html'

#delete milestone
class MilestoneDelete(DeleteView):
    template_name = 'uks_app/delete_issue.html'
    model = Milestone

    def dispatch(self, request, *args, **kwargs):
       entity = get_object_or_404(Milestone, pk=kwargs['pk'])
       user = request.user
       observed_project = entity.project

       if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
           return HttpResponse('Unauthorized', status=401)
       return super(MilestoneDelete, self).dispatch(request, *args, **kwargs)

    success_url = reverse_lazy('all_projects')

# new milestone
@login_required
def create_update_milestone(request, project_id, milestone_id=None):

    #get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
        #milestone_id == None -> Create
        #milestone_id != None -> Update
    observed_milestone = get_object_or_404(Milestone, pk=milestone_id) if milestone_id else None

    form = MilestoneForm(request.POST or None, instance=observed_milestone)

    if form.is_valid():
        milestone = form.save(commit=False)
        
        #set project as foreign key
        milestone.project = observed_project
        milestone.save()
        
        if milestone_id:
            return HttpResponseRedirect('/project/' + str(project_id) + '/milestone/' + str(milestone_id) + '/')  
        else:
            return HttpResponseRedirect('/project/' + str(project_id) + '/milestone/' + str(milestone.id) + '/')  

    context = {
        'form' : form,
    }
    return render(request, 'uks_app/create_update_milestone.html', context)
    
   


# choose milestone
@login_required
def choose_milestone(request, issue_id):
    
    #get issue and project
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)

    form = ChooseMilestoneForm(observed_project, observed_issue, data=request.POST or None)

    user = request.user

    if form.is_valid():
    
        chosen_milestones = form.cleaned_data['milestones']
        
        for milestone in chosen_milestones:
            milestone_change = MilestoneChange.objects.create(time = datetime.datetime.now(), user = user, issue = observed_issue, checkpoint=milestone, add=True) 
            milestone_change.save()
            #observed_issue.milestonechanges.add(milestone_change)
            #observed_issue.save()

            milestone.issue.add(observed_issue)
            milestone.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = { 
         'form' : form,
         'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_milestone.html', context)

@login_required
def remove_milestone(request, milestone_id, issue_id):

    #get issue
    issue = get_object_or_404(Issue, id=issue_id)
    observed_project = issue.project
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    #get milestone
    milestone = get_object_or_404(Milestone, id=milestone_id)

    issue.milestones.remove(milestone)

    user = request.user
    milestone_change = MilestoneChange.objects.create(time = datetime.datetime.now(), user = user, issue = issue, checkpoint=milestone, add=False) 

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/') 

# new comment form
@login_required
def create_update_comment(request, issue_id, comment_id=None):
    observed_issue = get_object_or_404(Issue, id=issue_id)  #get issue
    observed_project = observed_issue.project
    # only project owner and collaborators can create comments
    if observed_project.public == False and request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)

    #comment_id == None -> Create
    #comment_id != None -> Update
    observed_comment = get_object_or_404(Comment, pk=comment_id) if comment_id else None

    initial = ''

    if observed_comment:
        initial = observed_comment.description

        comment_changes = observed_comment.commentchange_set.all()
        print(comment_changes)

        if comment_changes:
            initial = comment_changes.reverse()[0]

    form = CommentForm(request.POST or None, instance=observed_comment, initial={'description': initial})
    #form.fields["description"].initial = 'initialllll'

    user = request.user

    if form.is_valid():

        if comment_id:
            if (user == observed_comment.user):
                comment = form.save(commit=False)
                commentChange = CommentChange(comment = comment, newComment=comment.description, time = datetime.datetime.now())
                commentChange.save()
            else:
                return HttpResponse('Unauthorized', status=401)
        else:
            comment = form.save(commit=False)            
            #set issue as foreign key
            comment.issue = observed_issue
            comment.time = datetime.datetime.now()
            comment.user = user
            comment.save()
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')  

    cancel_url = "../../../../../issue/"+str(issue_id) if issue_id else "../../"

    context = {
        'form' : form,
        'cancel_url': cancel_url
    }
    return render(request, 'uks_app/create_update_comment.html', context)

# delete comment
@login_required
def comment_delete_view(request, issue_id, comment_id):
    observed_issue = get_object_or_404(Issue, id=issue_id)  #get issue
    user = request.user
    observed_comment = get_object_or_404(Comment, id=comment_id)
    if (user == observed_comment.user):           
        observed_comment.delete()
    else:
        return HttpResponse('Unauthorized', status=401)
    return HttpResponseRedirect('/issue/' + str(issue_id) + '/') 

# one comment detailed view
class OneCommentView(generic.DetailView):
    model = Comment
    template_name = 'uks_app/one_comment.html'

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, project_id, format=None):
        data = {}
        temp_data = []

        issues = Issue.objects.filter(project_id=project_id).all()
        for issue in issues:

            create_date = issue.create_time.date()

            temp_data.append((str(create_date), 'open'))

            events = Event.objects.filter(issue_id=issue.id).order_by('time')

            for event in events:
                if event.__class__.__name__ == 'IssueChange':
                    date = event.time.date()
                    if event.state == 'CL':
                        temp_data.append((str(date), 'close'))
                    else:
                        temp_data.append((str(date), 'open'))

        opened_issues = 0

        sorted_data = sorted(temp_data, key=lambda x: x[0])

        for entry in sorted_data:
            if entry[1] == 'open':
                opened_issues += 1
            else:
                opened_issues -= 1
            data[str(entry[0])] = opened_issues


        labels = [] 
        values = []

        for i in sorted (data.keys()) :  
            labels.append(i)
            values.append(data[i])

        response_data = {
            "labels": labels,
            "values": values,
        }
        return Response(response_data)

 
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


    return HttpResponse('Unauthorized', status=401)  

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