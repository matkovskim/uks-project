from django.contrib import admin
from django.contrib.auth.models import User
# Register your models here.
from .models import ObservedProject, Issue, Label, Comment, Milestone, User, MilestoneChange, CodeChange, ResponsibleUserChange, StateChange, Profile, Event

admin.site.register(ObservedProject)
admin.site.register(Issue)
admin.site.register(Label)
admin.site.register(Comment)
admin.site.register(Milestone)
admin.site.register(MilestoneChange)
admin.site.register(CodeChange)
admin.site.register(ResponsibleUserChange)
admin.site.register(StateChange)
admin.site.register(Event)
admin.site.register(Profile)

