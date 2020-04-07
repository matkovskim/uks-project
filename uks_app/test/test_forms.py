from django.test import SimpleTestCase
from uks_app.forms import MilestoneForm, ProjectForm, LabelForm, CommentForm, IssueForm
from uks_app.models import Issue, ObservedProject, User
import datetime

class TestMilestoneForms(SimpleTestCase):

    def test_milestone_form_valid_data(self):
        form = MilestoneForm(data={
            'title': 'some title',
            'date' : '2020-02-15 15:04:12.718131',
            'description' : 'some description'
        })

        self.assertTrue(form.is_valid())

    def test_milestone_form_no_data(self):
        form = MilestoneForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

class TestProjectForms(SimpleTestCase):

    def test_project_form_valid_data(self):

        form = ProjectForm(data = {
            'name': 'project',
            'git_repo': 'git_repo',
            'description' : 'description',
            'public' : True
        })

        self.assertTrue(form.is_valid())

    def test_project_form_no_data(self):

        form = ProjectForm(data = {})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

class TestLabelForms(SimpleTestCase):
    
    def test_create_label_form_valid_data(self):
        form = LabelForm(data = {
            'name' : 'Labela test',
            'color' : '#eb34e8'
        })

        self.assertTrue(form.is_valid())

    def test_create_label_form_no_data(self):
        form = LabelForm(data = {})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),2)

class TestCommentForms(SimpleTestCase):

    def test_comment_form_valid_data(self):
        form = CommentForm(data={
            'description': 'some description'
        })

        self.assertTrue(form.is_valid())

    def test_comment_form_no_data(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

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