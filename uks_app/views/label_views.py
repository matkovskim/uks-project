import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from uks_app.models import Issue, Label, LableEvent
from uks_app.forms import LabelForm, ChooseLabelForm

# create a new label
@login_required
def create_label(request, issue_id):

    # get issue
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

        q = LableEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, label=label, state="CR")
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_label.html', context)
    
# choose one of the existing lables in the project
@login_required
def choose_label(request, issue_id):

    # get issue and project
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
            q = LableEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, label=label, state="CR")
        
        return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

    context = {
        'form' : form,
        'issue' : observed_issue
    }

    return render(request, 'uks_app/choose_label.html', context)

# remove a label
@login_required
def remove_label(request, label_id, issue_id):

    # get issue
    issue = get_object_or_404(Issue, id=issue_id)
    observed_project = issue.project

    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    # get label
    label = get_object_or_404(Label, id=label_id)

    issue.labels.remove(label)

    LableEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=issue, label=label, state="RE")

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')
