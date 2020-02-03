from django import forms

from .models import ObservedProject, Issue

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