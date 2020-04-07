from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.views import generic
from django.urls import reverse_lazy

from uks_app.models import ObservedProject, Issue
from uks_app.forms import ProjectForm

# create a new project or update an existing project
@login_required
def create_update_project(request, project_id=None):
 
    user = request.user

    # project_id == None -> Create
    # project_id != None -> Update
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
            return HttpResponseRedirect('/project/' + str(project.id) + '/') 

    context = {
        'form' : form,
    }

    return render(request, 'uks_app/create_update_project.html', context)

# delete an existing project
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

# view all public projects
class ProjectView(generic.ListView):
    template_name = 'uks_app/all_projects.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return ObservedProject.objects.filter(public=True).all()

# view one project - detail view
class OneProjectView(generic.DetailView):
    model = ObservedProject
    template_name = 'uks_app/one_project.html'

    def dispatch(self, request, *args, **kwargs):
        entity = get_object_or_404(ObservedProject, pk=kwargs['pk'])
        user = request.user

        if not entity.public and user != entity.user and not entity.collaborators.filter(id = user.id).exists():
            return HttpResponse('Unauthorized', status=401)
        return super(OneProjectView, self).dispatch(request, *args, **kwargs)
