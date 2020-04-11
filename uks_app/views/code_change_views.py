import re
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from uks_app.models import ObservedProject, Issue, User, CodeChange, CodeChangeEvent
import json

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
                message_parts = message.split('\n\n')
                title=message_parts[0]
                message=""
                if len(message_parts)>1:
                    message=message_parts[1]
                if len(users)==0:
                    q = CodeChange.objects.create(url=commit_url, project=project.first(), title=title, message=message, date_time=time, github_username=username)
                else:
                    q = CodeChange.objects.create(url=commit_url, project=project.first(), title=title, message=message, user=users[0], date_time=time, github_username=username)
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
