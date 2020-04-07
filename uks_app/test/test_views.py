from django.test import TestCase, Client
from django.urls import reverse
from uks_app.models import Comment, Issue, User, ObservedProject, CommentChange, Milestone, Label
from django.contrib.auth.models import User
import json 
from django.utils import timezone

class TestMilestoneViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john', 'john@uks.com', 'johnpassword')
        self.user1 = User.objects.create_user('milos', 'milos@uks.com', 'milos')
        self.project = ObservedProject.objects.create(user=self.user, name='uks', git_repo='https://github.com/matkovskim/uks-project', description='some description for project', public=True)
        self.project2 = ObservedProject.objects.create(user=self.user, name='jsd', git_repo='https://github.com/matkovskim/jsd-project', description='some description for project', public=True)

        self.issue = Issue.objects.create(title='Crud comments', project=self.project, description='some description for issue', state=0, create_time='2020-02-15 15:04:12.718131+01')
        self.create_milestone_url = reverse('new_milestone', args=[self.project.id])

    def test_create_milestone_logged_get(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        response_get = self.client.get(self.create_milestone_url)      
        self.assertEquals(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'uks_app/create_update_milestone.html')

    def test_create_milestone_not_logged(self):       
        response = self.client.get(self.create_milestone_url)
        self.assertEquals(response.status_code, 302) # redirect

    def test_create_milestone_logged(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        response = self.client.post(self.create_milestone_url, {
            'title': 'some title',
            'description': 'some description',
            'date': '2020-02-15 15:04:12.718131'
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Milestone.objects.first().description, 'some description')
        self.assertEquals(Milestone.objects.first().title, 'some title')
        self.assertEquals(Milestone.objects.first().project, self.project)

    def test_create_milestone_logged_no_data(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        response = self.client.post(self.create_milestone_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Comment.objects.count(), 0)

    def test_update_milestone_logged(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        milestone = Milestone.objects.create(project=self.project, title='some title', description='some description', date = '2020-02-15 15:04:12.718131')
        edit_milestone_url = reverse('edit_milestone', args=[self.project.id, milestone.id])
        response = self.client.post(edit_milestone_url, { 
            'title': 'some title',           
            'description': 'new description',
            'date': '2020-02-15 15:04:12.718131'
        })
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Milestone.objects.first().description, 'new description')

    def test_delete_milestone_logged(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        milestone = Milestone.objects.create(project=self.project, title='some title', description='some description', date = '2020-02-15 15:04:12.718131')
        delete_url = reverse('delete_milestone', args=[self.project.id, milestone.id])
        self.assertEquals(Milestone.objects.count(), 1)
        response = self.client.delete(delete_url)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Milestone.objects.count(), 0)

    def test_one_milestone(self):
        milestone = Milestone.objects.create(project=self.project, title='some title', description='some description', date = '2020-02-15 15:04:12.718131')
        one_milestone_url = reverse('one_milestone', args=[self.project.id, milestone.id])
        response = self.client.get(one_milestone_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/one_milestone.html')

class TestProjectViews(TestCase):

    def setUp(self):
        self.client = Client()

        self.us = User.objects.create_user('majak', 'majak@uks.com', 'pass')
        self.us.save()

        self.johnus = User.objects.create_user('john', 'john@uks.com', 'johnpass')
        self.johnus.save()

    def test_project_list_GET(self):

        response = self.client.get(reverse('all_projects'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/all_projects.html')

    def test_project_public_GET(self):

        ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            id = 1,
            user = self.us
        )
        
        response = self.client.get(reverse('one_project', args=['1']))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/one_project.html')

    def test_project_private_GET_unauthorized(self):

        ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = False,
            id = 1,
            user = self.us
        )
        
        response = self.client.get(reverse('one_project', args=['1']))

        self.assertEquals(response.status_code, 401)

    def test_project_private_GET_authorized(self):

        self.client.login(username='majak', password='pass')

        ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = False,
            id = 1,
            user = self.us
        )
        
        response = self.client.get(reverse('one_project', args=['1']))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/one_project.html')
        
    def test_project_create_POST_authorized(self):

        self.client.login(username='majak', password='pass')
    
        response = self.client.post(reverse('new_project'), 
        {
            'name' : 'project1',
            'git_repo' : 'git_repo',
            'description' : 'description',
            'public' : True          
        })

        self.assertEquals(response.status_code, 302)
        project = ObservedProject.objects.first()
        self.assertEquals(project.name, 'project1')
        self.assertEquals(project.git_repo, 'git_repo')
        self.assertEquals(project.description, 'description')
        self.assertEquals(project.user, self.us)
        self.assertEquals(project.public, True)

    def test_project_create_POST_unauthorized(self):
    
        response = self.client.post(reverse('new_project'), 
        {
            'name' : 'project1',
            'git_repo' : 'git_repo',
            'description' : 'description',
            'public' : True          
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(ObservedProject.objects.count(), 0)

    def test_project_create_POST_no_data(self):

        self.client.login(username='majak', password='pass')

        response = self.client.post(reverse('new_project'))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ObservedProject.objects.count(), 0)

    def test_project_DELETE_unauthorized(self):

        ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            id = 1,
            user = self.us
        )

        response = self.client.delete(reverse('delete_project', kwargs={'pk': 1}))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(ObservedProject.objects.count(), 1)

    def test_project_DELETE_not_owner(self):

        self.client.login(username='john', password='johnpass')

        ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            id = 1,
            user = self.us
        )

        response = self.client.delete(reverse('delete_project', kwargs={'pk': 1}))

        self.assertEquals(response.status_code, 401)
        self.assertEquals(ObservedProject.objects.count(), 1)

    def test_project_DELETE_owner(self):

        self.client.login(username='majak', password='pass')

        ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            id = 1,
            user = self.us
        )

        response = self.client.delete(reverse('delete_project', kwargs={'pk': 1}))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(ObservedProject.objects.count(), 0)

    def test_project_UPDATE_owner(self):
        self.client.login(username='majak', password='pass')

        proj = ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            user = self.us
        )
   
        response = self.client.post(reverse('edit_project', args=[proj.id]), { 
            'name' : 'project_new',
            'git_repo' :'git_new',
            'description' : 'description_new',
            'public' : True,
        })
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(ObservedProject.objects.first().name, 'project_new')
        self.assertEquals(ObservedProject.objects.first().git_repo, 'git_new')
        self.assertEquals(ObservedProject.objects.first().description, 'description_new')

    def test_project_UPDATE_not_owner(self):
        self.client.login(username='john', password='johnpass')

        proj = ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            user = self.us
        )
   
        response = self.client.post(reverse('edit_project', args=[proj.id]), { 
            'name' : 'project_new',
            'git_repo' :'git_new',
            'description' : 'description_new',
            'public' : True,
        })
        
        self.assertEquals(response.status_code, 401)
        self.assertEquals(ObservedProject.objects.first().name, 'project')
        self.assertEquals(ObservedProject.objects.first().git_repo, 'git_repo')
        self.assertEquals(ObservedProject.objects.first().description, 'description')

    def test_project_UPDATE_unauthorized(self):

        proj = ObservedProject.objects.create(
            name='project',
            git_repo='git_repo',
            description='description',
            public = True,
            user = self.us
        )
   
        response = self.client.post(reverse('edit_project', args=[proj.id]), { 
            'name' : 'project_new',
            'git_repo' :'git_new',
            'description' : 'description_new',
            'public' : True,
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(ObservedProject.objects.first().name, 'project')
        self.assertEquals(ObservedProject.objects.first().git_repo, 'git_repo')
        self.assertEquals(ObservedProject.objects.first().description, 'description')
        
class TestLabelViews(TestCase):
    
    def setUp(self):
        self.client = Client()

        self.us = User.objects.create_user('vesnamilic', 'vesna@uks.com', 'pass')
        self.us.save()

        self.us2 = User.objects.create_user('user2', 'user2@uks.com', 'pass')
        self.us2.save()

        self.client.login(username='vesnamilic', password='pass')

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

        self.label = Label.objects.create(
            name = 'Label 1',
            color = '#fffff'
        )

        self.label.save()
        self.label.issue.add(self.issue)

        self.create_label_url = reverse('new_label', args=[self.issue2.id])
        self.remove_label_url = reverse('remove_label', args=[self.issue.id,self.label.id])


    def test_create_label_GET(self):
        response = self.client.get(self.create_label_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/create_label.html')

    
    def test_create_label_POST(self):
        response = self.client.post(self.create_label_url, {
            'name' : 'Label create',
            'color' : '#4287f5'
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.issue2.labels.first().name, 'Label create')


    def test_create_label_POST_invalid(self):
        response = self.client.post(self.create_label_url, {
            'color' : '#4287f5'
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.issue2.labels.count(), 0)

    def test_create_label_POST_unauthorized(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.create_label_url, {
            'name' : 'Label create',
            'color' : '#4287f5'
        })

        self.assertEquals(response.status_code, 401)
        self.assertEquals(self.issue2.labels.count(), 0)

    def test_create_label_POST_login_required(self):
        self.client.logout()

        response = self.client.post(self.create_label_url, {
            'name' : 'Label create',
            'color' : '#4287f5'
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.issue2.labels.count(), 0)

    def test_remove_label_POST(self):
        response = self.client.post(self.remove_label_url)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.issue.labels.count(), 0)

    def test_remove_label_404(self):
        response = self.client.post(reverse('remove_label', args=[self.issue.id,100]))
        self.assertEquals(response.status_code, 404)


    def test_remove_label_POST_login_required(self):
        self.client.logout()

        response = self.client.post(self.remove_label_url)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.issue.labels.count(), 1)

    def test_remove_label_POST_login_unauthorized(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.remove_label_url)

        self.assertEquals(response.status_code, 401)
        self.assertEquals(self.issue.labels.count(), 1)

class TestCommentViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john', 'john@uks.com', 'johnpassword')
        self.user1 = User.objects.create_user('jelena', 'jelena@uks.com', 'jelena')
        self.project = ObservedProject.objects.create(user=self.user, name='uks', git_repo='https://github.com/matkovskim/uks-project', description='some description for project', public=True)
        self.issue = Issue.objects.create(title='Crud comments', project=self.project, description='some description for issue', state=0, create_time='2020-02-15 15:04:12.718131+01')
        self.create_comment_url = reverse('new_comment', args=[self.issue.id])
        self.issue2 = Issue.objects.create(title='Crud comments2', project=self.project, description='some description for issue', state=0, create_time='2020-02-15 15:04:12.718131+01')

    def test_create_comment_logged_get(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        response_get = self.client.get(self.create_comment_url)      
        self.assertEquals(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'uks_app/create_update_comment.html')

    def test_create_comment_not_logged(self):       
        response = self.client.get(self.create_comment_url)
        self.assertEquals(response.status_code, 302) # redirect

    def test_create_comment_logged(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        response = self.client.post(self.create_comment_url, {
            'description': 'comment 1'
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Comment.objects.first().description, 'comment 1')
        self.assertEquals(Comment.objects.first().user, self.user)
        self.assertEquals(Comment.objects.first().issue, self.issue)

    def test_create_comment_logged_no_data(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        response = self.client.post(self.create_comment_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Comment.objects.count(), 0)

    def test_update_comment_logged(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        edit_comment_url = reverse('edit_comment', args=[self.issue.id, comment.id])
        response = self.client.post(edit_comment_url, {            
            'description': 'new description'
        })
        
        self.assertEquals(response.status_code, 302)
        self.assertEquals(CommentChange.objects.first().newComment, 'new description')

    def test_update_comment_wrong_user(self):
        self.client.login(username='jelena', password='jelena') # user must be logged in
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        edit_comment_url = reverse('edit_comment', args=[self.issue.id, comment.id])
        response = self.client.post(edit_comment_url, {            
            'description': 'new description'
        })
        
        self.assertEquals(response.status_code, 401)
        self.assertEquals(CommentChange.objects.count(), 0)
    
    def test_update_comment_wrong_issue(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        edit_comment_url = reverse('edit_comment', args=[self.issue2.id, comment.id])
        response = self.client.post(edit_comment_url, {            
            'description': 'new description'
        })
        self.assertEquals(response.status_code, 401)
        self.assertEquals(CommentChange.objects.count(), 0)

    def test_delete_comment_logged(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        delete_comment_url = reverse('delete_comment', args=[self.issue.id, comment.id])
        self.assertEquals(Comment.objects.count(), 1)
        response = self.client.delete(delete_comment_url)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Comment.objects.count(), 0)

    def test_delete_comment_wrong_user(self):
        self.client.login(username='jelena', password='jelena') # user must be logged in
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        delete_comment_url = reverse('delete_comment', args=[self.issue.id, comment.id])
        self.assertEquals(Comment.objects.count(), 1)
        response = self.client.delete(delete_comment_url)
        self.assertEquals(response.status_code, 401)
        self.assertEquals(Comment.objects.count(), 1)

    def test_delete_comment_wrong_issue(self):
        self.client.login(username='john', password='johnpassword') # user must be logged in
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        delete_comment_url = reverse('delete_comment', args=[self.issue2.id, comment.id])
        self.assertEquals(Comment.objects.count(), 1)
        response = self.client.delete(delete_comment_url)
        self.assertEquals(response.status_code, 401)
        self.assertEquals(Comment.objects.count(), 1)

    def test_one_comment(self):
        comment = Comment.objects.create(issue=self.issue, user=self.user, description='some description', time='2020-02-15 15:04:12.718131+01')
        one_comment_url = reverse('one_comment', args=[comment.id])
        response = self.client.get(one_comment_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'uks_app/one_comment.html')

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

    def test_create_issue_no_project_POST(self):
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