from django.db import models
from django.contrib.auth.models import User
from PIL import Image 
from polymorphic.models import PolymorphicModel

OPEN='OP'
CLOSED='CL'
PROBLEM_STATE = (
    (OPEN, 'Open'),
    (CLOSED, 'Closed')
)

class ObservedProject(models.Model):
    user = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False)
    git_repo = models.CharField(max_length=200, blank=False)
    description = models.TextField(max_length=200, blank=True)
    public=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Issue(models.Model):
    title = models.CharField(max_length=200, blank=False)
    project = models.ForeignKey(to=ObservedProject, null=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=200, blank=True)
    parent_issue = models.ForeignKey('self', null=True, related_name='subissues', on_delete=models.CASCADE)
    state = models.CharField(
        max_length=2,
        choices=PROBLEM_STATE,
        default=OPEN,
    )
    create_time = models.DateTimeField()
    
    def __str__(self):
        return self.title

class Label(models.Model):
    name = models.CharField(max_length=200, blank=False)
    color = models.CharField(max_length=200, blank=False)
    issue = models.ManyToManyField(Issue, related_name='labels')

    def __str__(self):
        return self.name


class Milestone(models.Model):
    title = models.CharField(max_length=200, blank=False)
    date = models.DateTimeField()
    description = models.TextField(max_length=200, blank=True)
    project = models.ForeignKey(to=ObservedProject, null=False, on_delete=models.CASCADE)
    issue = models.ManyToManyField(Issue, related_name='milestones')

    def __str__(self):
        return str(self.title)
 
class Event(PolymorphicModel):
    time = models.DateTimeField()
    user = models.ForeignKey(to=User, null=True, on_delete=models.CASCADE)
    issue = models.ForeignKey(to=Issue, null=False, on_delete=models.CASCADE)

class Comment(Event):
    description = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.description

class CommentChange(models.Model):
    comment = models.ForeignKey(to=Comment, null=False, on_delete=models.CASCADE)
    newComment = models.CharField(max_length=200, blank=False)
    time = models.DateTimeField()
    class Meta:
        ordering = ['time']

    def __str__(self):
        return self.newComment

class CodeChange(models.Model):
    url = models.CharField(max_length=200, blank=False)
    message = models.CharField(max_length=400)
    project = models.ForeignKey(to=ObservedProject, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, null=True, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    github_username = models.CharField(max_length=200, blank=False)
    def __str__(self):
        return self.url

class CodeChangeEvent(Event):
    code_change = models.ForeignKey(to=CodeChange, null=False, on_delete=models.CASCADE)
    closing_event = models.BooleanField(default=False)

class IssueChange(Event):
    state = models.CharField(
        max_length=2,
        choices=PROBLEM_STATE,
        default=OPEN,
    )

class MilestoneChange(Event):
    add = models.BooleanField()
    checkpoint = models.ForeignKey(to=Milestone, null=False, on_delete=models.CASCADE)

class ResponsibleUserChange(Event):
    responsibleUser = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.responsibleUser.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

