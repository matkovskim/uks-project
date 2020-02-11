from django import forms

from .models import ObservedProject, Issue, Comment

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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'description',
            'user'
        ]