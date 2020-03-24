from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic

from uks_app.models import Issue, Comment, CommentChange
from uks_app.forms import CommentForm

import datetime

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
            if (user == observed_comment.user and observed_comment.issue.id == issue_id):
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
    if (user == observed_comment.user and observed_issue == observed_comment.issue):           
        observed_comment.delete()
    else:
        return HttpResponse('Unauthorized', status=401)
    return HttpResponseRedirect('/issue/' + str(issue_id) + '/') 

# one comment detailed view
class OneCommentView(generic.DetailView):
    model = Comment
    template_name = 'uks_app/one_comment.html'

    def dispatch(self, request, *args, **kwargs):
        entity = get_object_or_404(Comment, pk=kwargs['pk'])
        user = request.user

        if not entity.issue.project.public and user != entity.issue.project.user and not entity.issue.project.collaborators.filter(id = user.id).exists():
            return HttpResponse('Unauthorized', status=401)
        return super(OneCommentView, self).dispatch(request, *args, **kwargs)
