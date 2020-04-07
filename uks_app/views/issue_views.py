import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.views import generic
from django.urls import reverse_lazy

from uks_app.models import ObservedProject, Issue, IssueChange, Event, SubIssueEvent, AssignIssueEvent
from uks_app.forms import IssueForm, AssignIssueForm

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# create a new issue or update an existing issue
@login_required
def create_update_issue(request, project_id, issue_id=None):

    # get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    # issue_id == None -> Create 
    # issue_id != None -> Update
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
        
        # set project as foreign key
        issue.project = observed_project
        issue.save()
        
        if issue_id == None and issue.parent_issue != None :
            SubIssueEvent.objects.create(user=request.user, time= datetime.datetime.now(), issue=issue.parent_issue, state="CR", subissue=issue)


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

# change the state of an issue
def change_issue_state(request, project_id, issue_id):

    # get observed project
    observed_project = get_object_or_404(ObservedProject, id=project_id)

    # only project owner and collaborators can change issue state
    if request.user != observed_project.user and not observed_project.collaborators.filter(id = request.user.id).exists():
        return HttpResponse('Unauthorized', status=401)
    
    # get issue
    observed_issue = get_object_or_404(Issue, id=issue_id)

    if observed_issue.state == "OP":
        observed_issue.state = "CL"
        q = IssueChange.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, state="CL")

    else:
        observed_issue.state = "OP"
        q = IssueChange.objects.create(user=request.user, time= datetime.datetime.now(), issue=observed_issue, state="OP")
    
    observed_issue.save()

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

# assign an issue to a user
@login_required
def assign_issue(request, issue_id):

    # get issue and project
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

# delete an existing issue
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

# view one issue - detail view
class OneIssueView(generic.DetailView):
    model = Issue
    template_name = 'uks_app/one_issue.html'

    def get_context_data(self, **kwargs):
        context = super(OneIssueView, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(issue_id=self.kwargs.get('pk')).order_by('time')

        return context
    
    def dispatch(self, request, *args, **kwargs):
        entity = get_object_or_404(Issue, pk=kwargs['pk'])
        user = request.user

        if not entity.project.public and user != entity.project.user and not entity.project.collaborators.filter(id = user.id).exists():
            return HttpResponse('Unauthorized', status=401)
        return super(OneIssueView, self).dispatch(request, *args, **kwargs)

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

