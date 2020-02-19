from django.test import TestCase, Client
from django.urls import reverse
from uks_app.models import Comment, Issue, User, ObservedProject, CommentChange, Milestone
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