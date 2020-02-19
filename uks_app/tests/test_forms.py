from django.test import SimpleTestCase
from uks_app.forms import IssueForm
from uks_app.models import Issue, ObservedProject, User
import datetime

class TestIssuesForms(SimpleTestCase):

    def test_issue_form_valid_data(self):
        
        us = User('marijana', 'marijana@uks.com', 'pass')

        observed_project = ObservedProject(
            name = 'Project 1',
            git_repo = 'https://github.com/project1',
            description = 'Description',
            public = True,
            user=us
        )
        
        observed_issue = Issue(
            title = 'Issue 1',
            description = 'Opis',
            project = observed_project,
            create_time = datetime.datetime.now(),
            parent_issue=None
        )        
        
        form=IssueForm(
            data={
            'title':'issue 2',
            'description':'description issue1'
            }, project=observed_project, iss=observed_issue, instance=observed_issue
        )

        self.assertTrue(form.is_valid())

    def test_issue_form_not_valid_data(self):
        
        us = User('marijana', 'marijana@uks.com', 'pass')

        observed_project = ObservedProject(
            name = 'Project 1',
            git_repo = 'https://github.com/project1',
            description = 'Description',
            public = True,
            user=us
        )
        
        observed_issue = Issue(
            title = 'Issue 1',
            description = 'Opis',
            project = observed_project,
            create_time = datetime.datetime.now(),
            parent_issue=None
        )

        form=IssueForm(
            data={}, project=observed_project, iss=observed_issue, instance=observed_issue
        )

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)