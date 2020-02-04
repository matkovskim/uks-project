from django.db import models

OPEN='OP'
CLOSED='CL'
PROBLEM_STATE = (
    (OPEN, 'Open'),
    (CLOSED, 'Closed')
)

class ObservedProject(models.Model):
    name = models.CharField(max_length=200, blank=False)
    git_repo = models.CharField(max_length=200, blank=False)
    description = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class Issue(models.Model):
    title = models.CharField(max_length=200, blank=False)
    project = models.ForeignKey(to=ObservedProject, null=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=200, blank=True)
    state = models.CharField(
        max_length=2,
        choices=PROBLEM_STATE,
        default=OPEN,
    )

    def __str__(self):
        return self.title

class Label(models.Model):
    name = models.CharField(max_length=200, blank=False)
    color = models.CharField(max_length=200, blank=False)
    project = models.ForeignKey(to=ObservedProject, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=200, blank=False)
    email = models.CharField(max_length=200, blank=False)
    
    def __str__(self):
        return self.name

class Milestone(models.Model):
    title = models.CharField(max_length=200, blank=False)
    date = models.DateField()
    description = models.TextField(max_length=200, blank=True)
    project = models.ForeignKey(to=ObservedProject, null=False, on_delete=models.CASCADE)
 
    def __str__(self):
        return str(self.date)
 
class Event(models.Model):
    time = models.DateField()
    user = models.ForeignKey(to=User, null=True, on_delete=models.CASCADE)
    issue = models.ForeignKey(to=Issue, null=False, on_delete=models.CASCADE)

class Comment(Event):
    description = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.description

class CommentChange(Event):
    newComment = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.newComment

class CodeChange(Event):
    url = models.URLField(max_length=100)

    def __str__(self):
        return self.url

class StateChange(Event):
    newState = models.CharField(max_length=6, choices=PROBLEM_STATE, default=OPEN)
    
    def __str__(self):
        return self.newState

class MilestoneChange(Event):
    checkpoint = models.ForeignKey(to=Milestone, null=False, on_delete=models.CASCADE)

class ResponsibleUserChange(Event):
    responsibleUser = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.responsibleUser.name