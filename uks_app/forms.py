from django import forms

from .models import ObservedProject, Issue, Profile, Milestone, Label, Comment
from django.forms.widgets import TextInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    
    class Meta:
        labels = {
            "public": "Make this repository public"
        }
        model = ObservedProject
        fields = [
            'name',
            'git_repo',
            'description',
            'public'
        ]
        

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            'title',
            'description',
            'parent_issue'
        ]

    def __init__(self, project, iss, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)

        if iss == None:
            issues = project.issue_set.all()

            self.fields['parent_issue'] = forms.ModelChoiceField(queryset=issues, required=False) 
        else:
            del self.fields['parent_issue']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'description',
        ]

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = [
            'title',
            'date',
            'description'
        ]

    def __init__(self, *args, **kwargs):
        super(MilestoneForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datepicker'

class ChooseMilestoneForm(forms.Form): 

    def __init__(self, project, observed_issue, *args, **kwargs):
        super(ChooseMilestoneForm, self).__init__(*args, **kwargs)

        milestones = Milestone.objects.filter(project = project).exclude(id__in=[milestone.id for milestone in observed_issue.milestones.all()]).all()

        self.fields['milestones'] = forms.ModelMultipleChoiceField(queryset=milestones) 

    def save(self, commit=True):
        print(self.fields['milestones'])

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = [
            'name',
            'color'
        ]
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }

class ChooseLabelForm(forms.Form): 

    def __init__(self, project_issues, observed_issue, *args, **kwargs):
        super(ChooseLabelForm, self).__init__(*args, **kwargs)

        labels = Label.objects.filter(issue__in=[issue.id for issue in project_issues]).exclude(id__in=[label.id for label in observed_issue.labels.all()]).distinct()

        self.fields['labels'] = forms.ModelMultipleChoiceField(queryset=labels)

    def save(self, commit=True):
        print(self.fields['labels'])

class ChooseSubissueForm(forms.Form): 

    def __init__(self, observed_issue, *args, **kwargs):
        super(ChooseSubissueForm, self).__init__(*args, **kwargs)

        issues = observed_issue.project.issue_set.exclude(id=observed_issue.id).exclude(parent_issue__isnull=False).exclude(subissues__isnull=False)

        if observed_issue.parent_issue:
            issues = issues.exclude(id=observed_issue.parent_issue.id)

        self.fields['issues'] = forms.ModelMultipleChoiceField(queryset=issues)

    def save(self, commit=True):
        print(self.fields['issues'])


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name'
        ]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
