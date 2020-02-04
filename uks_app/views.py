from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from .models import ObservedProject, Issue, Label
from .forms import ProjectForm, IssueForm, LabelForm, ChooseLabelForm

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
def create_label(request, issue_id):

    #get issue
    observed_issue = get_object_or_404(Issue, pk=issue_id)

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
def choose_label(request, issue_id):

    #get issue and project
    observed_issue = get_object_or_404(Issue, pk=issue_id)
    observed_project = observed_issue.project

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

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')


def remove_label(request, label_id, issue_id):

    #get issue
    issue = get_object_or_404(Issue, id=issue_id)

    #get label
    label = get_object_or_404(Label, id=label_id)

    issue.labels.remove(label)

    if label.issue.count() <= 0:
        label.delete()

    return HttpResponseRedirect('/issue/' + str(issue_id) + '/')

#delete project
class ProjectDelete(DeleteView):
    template_name = 'uks_app/delete_project.html'
    model = ObservedProject

    success_url = reverse_lazy('all_projects')

#delete issue
class IssueDelete(DeleteView):
    template_name = 'uks_app/delete_issue.html'
    model = Issue

    def get_success_url(self):
        project = self.object.project
        return reverse_lazy( 'one_project', kwargs={'pk': project.id})

#delete label
#class LabelDelete(DeleteView):
#   model = Label
#
#   def get(self, *args, **kwargs):
#        return self.post(*args, **kwargs)
#
#    def get_success_url(self):
#        issue = self.object.issue
#        return reverse_lazy( 'one_issue', kwargs={'pk': issue.id, 'project_id': issue.project.id})

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