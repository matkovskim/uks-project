from django.test import TestCase, Client
from django.urls import reverse
from uks_app.models import ObservedProject, Label, Issue
from django.contrib.auth.models import User
import json 
from django.utils import timezone

class TestIssuesViews(TestCase):

    def setUp(self):

        self.us = User.objects.create_user('marijana', 'marijana@uks.com', 'pass')
        self.us.save()

        self.us2 = User.objects.create_user('user2', 'user2@uks.com', 'pass')
        self.us2.save()

        self.client.login(username='marijana', password='pass')

        self.project = ObservedProject.objects.create(
            name = 'TestProject',
            git_repo = 'github',
            description = 'description',
            public = False,
            user = self.us
        )
        self.project.save()

        self.issue = Issue.objects.create(
            title = 'Issue 1',
            description = 'Opis',
            project = self.project,
            create_time = timezone.now()
        )
        self.issue.save()

        self.issue2 = Issue.objects.create(
            title = 'Issue 2',
            description = 'Opis',
            project = self.project,
            create_time = timezone.now()
        )
        self.issue2.save()

        self.create_issue_url = reverse('new_issue', args=[self.project.id])
        self.create_issue_no_project_url = reverse('new_issue', args=[200]) 
        self.update_issue_url = reverse('edit_issue', args=[self.project.id, self.issue2.id])
        self.update_issue_no_project_url = reverse('edit_issue', args=[200, self.issue2.id])
        self.delete_issue_url = reverse('delete_issue', args=[self.issue2.id])
        self.delete_issue_no_issue_url = reverse('choose_label', args=[200])


    def test_create_issue_GET(self):
        response = self.client.get(self.create_issue_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/create_update_issue.html')

    def test_create_issue_POST(self):
        response = self.client.post(self.create_issue_url, {
            'title' : 'Issue name',
            'description' : 'decsription',
            'project':self.project
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Issue.objects.all().count(), 3)

    def test_edit_issue_no_project_POST(self):
        response = self.client.post(self.create_issue_no_project_url, {
            'title' : 'New issue name',
            'description' : 'new decsription'
        })
        
        self.assertEquals(response.status_code, 404)
     
    def test_create_issue_POST_invalid(self):
        response = self.client.post(self.create_issue_url, {
            'description' : 'decsription',
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Issue.objects.all().count(), 2)

    def test_create_issue_POST_login_required(self):
            self.client.logout()

            response = self.client.post(self.create_issue_url, {
                'title' : 'Issue name',
                'description' : 'decsription',
                'project':self.project
            })

            self.assertEquals(response.status_code, 302)
            self.assertEquals(Issue.objects.all().count(), 2)

    def test_create_issue_POST_login_unauthorized(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.create_issue_url)

        self.assertEquals(response.status_code, 401)
        self.assertEquals(Issue.objects.all().count(), 2)
    
    def test_edit_issue_POST(self):
        response = self.client.post(self.update_issue_url, {
            'title' : 'New issue name',
            'description' : 'new decsription',
            'project':self.project
        }, project_id=self.project.id, issue_id=self.issue2.id)
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Issue.objects.all().count(), 2)
        self.assertEquals(Issue.objects.get(id=self.issue2.id).title, 'New issue name')

    def test_edit_issue_POST_login_unauthorized(self):
        self.client.login(username='user2', password='pass')

        response = self.client.post(self.update_issue_url, {
            'title' : 'New issue name',
            'description' : 'new decsription',
            'project':self.project
        }, project_id=self.project.id, issue_id=self.issue2.id)
        
        self.assertEquals(response.status_code, 401)
        self.assertEquals(Issue.objects.all().count(), 2)
        self.assertEquals(Issue.objects.get(id=self.issue2.id).title, 'Issue 2')

    def test_edit_issue_no_project_POST(self):
        response = self.client.post(self.update_issue_no_project_url, {
            'title' : 'New issue name',
            'description' : 'new decsription',
            'project':self.project
        })
        
        self.assertEquals(response.status_code, 404)

    def test_delete_issue_error(self):
        response = self.client.post(self.delete_issue_no_issue_url)
        
        self.assertEquals(response.status_code, 404)

    def test_delete_issue(self):
        response = self.client.post(self.delete_issue_url)
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Issue.objects.all().count(), 1)

    def test_remove_issue_POST_login_unauthorized(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.delete_issue_url)

        self.assertEquals(response.status_code, 401)
        self.assertEquals(Issue.objects.all().count(), 2)
    