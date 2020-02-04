from django import forms
from django.forms.widgets import TextInput
from .models import ObservedProject, Issue, Label

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
