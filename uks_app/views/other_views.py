from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from uks_app.models import ObservedProject, Issue, Milestone, MilestoneChange, Event, Label, User, Comment, CommentChange, CodeChangeEvent, AssignIssueEvent, IssueChange, LableEvent, SubIssueEvent
from uks_app.forms import ProjectForm, IssueForm, MilestoneForm, LabelForm, ChooseLabelForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ChooseMilestoneForm, CommentForm, ChooseSubissueForm, AssignIssueForm
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from uks_app.models import ObservedProject, Issue, CodeChange
from uks_app.forms import ProjectForm, IssueForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

# home page
def index(request): 
    return render(request, 'uks_app/index.html') #optional third argument context

# one milestone detailed view
class OneMilestoneView(generic.DetailView):
    model = Milestone
    template_name = 'uks_app/one_milestone.html'

    def dispatch(self, request, *args, **kwargs):
        entity = get_object_or_404(Milestone, pk=kwargs['pk'])
        user = request.user

        if not entity.project.public and user != entity.project.user and not entity.project.collaborators.filter(id = user.id).exists():
            return HttpResponse('Unauthorized', status=401)
        return super(OneMilestoneView, self).dispatch(request, *args, **kwargs)

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

 
