from django import forms

from .models import ObservedProject, Issue

class ProjectForm(forms.ModelForm):
    class Meta:
        model = ObservedProject
        fields = [
            'name',
            'git_repo',
            'description',
        ]

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            'title',
            'description'
        ]