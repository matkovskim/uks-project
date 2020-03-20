import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.views import generic
from django.urls import reverse_lazy

from uks_app.models import ObservedProject, Issue, SubIssueEvent
from uks_app.forms import IssueForm, ChooseSubissueForm

# create a new subissue 
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

        q = SubIssueEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, state="CR", subissue=issue)
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')  
    
    context = {
        'form' : form,
        'cancel_url': "../"
    }

    return render(request, 'uks_app/create_update_issue.html', context)

# choose a subissue from existing issues
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
                
                q = SubIssueEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, state="CR", subissue=issue)
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
        'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_subissue.html', context)

# remove a subissue
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

    q = SubIssueEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=issue, state="RE", subissue=subissue)

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')