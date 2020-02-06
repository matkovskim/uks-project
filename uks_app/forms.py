from django import forms

from .models import ObservedProject, Issue, Profile, Milestone, Label
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
            'description'
        ]

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = [
            'title',
            'date',
            'description'
        ]
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
