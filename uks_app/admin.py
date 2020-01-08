from django.contrib import admin

# Register your models here.
from .models import ObservedProject, Issue, Label, Comment, Milestone, User, MilestoneChange, CodeChange, ResponsibleUserChange, StateChange

admin.site.register(ObservedProject)
admin.site.register(Issue)
admin.site.register(Label)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Milestone)
admin.site.register(MilestoneChange)
admin.site.register(CodeChange)
admin.site.register(ResponsibleUserChange)
admin.site.register(StateChange)

