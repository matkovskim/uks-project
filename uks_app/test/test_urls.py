from django.test import SimpleTestCase
from django.urls import reverse, resolve
from uks_app.views import *

class TestMilestoneUrls(SimpleTestCase):

    def test_new_milestone_url_resolves(self):
        url = reverse('new_milestone', args=['1'])
        self.assertEquals(resolve(url).func, create_update_milestone)
        
    def test_edit_milestone_url_resolves(self):
        url = reverse('edit_milestone', args=['1', '2'])
        self.assertEquals(resolve(url).func, create_update_milestone)
    
    def test_delete_milestone_url_resolves(self):
        url = reverse('delete_milestone', args=['1', '2'])
        self.assertEquals(resolve(url).func.view_class, MilestoneDelete)
    
    def test_one_milestone_url_resolves(self):
        url = reverse('one_milestone', args=['1', '2'])
        self.assertEquals(resolve(url).func.view_class, OneMilestoneView)

class TestProjectUrls(SimpleTestCase):

    def test_project_list_url(self):
        url = reverse('all_projects')
        self.assertEquals(resolve(url).func.view_class, ProjectView)

    def test_project_one_url(self):
        url = reverse('one_project', kwargs={'pk': 1})
        self.assertEquals(resolve(url).func.view_class, OneProjectView)
    
    def test_create_project_url(self):
        url = reverse('new_project')
        self.assertEquals(resolve(url).func, create_update_project)

    def test_update_project_url(self):
        url = reverse('edit_project', kwargs={'project_id': 1})
        self.assertEquals(resolve(url).func, create_update_project)

    def test_delete_project_url(self):
        url = reverse('delete_project', kwargs={'pk': 1})
        self.assertEquals(resolve(url).func.view_class, ProjectDelete)

class TestLabelUrls(SimpleTestCase):
    
    def test_list_url_is_resolves(self):
        url = reverse('new_label', args=[1])
        self.assertEquals(resolve(url).func, create_label)


    def test_remove_label_url_resolves(self):
        url = reverse('remove_label', args=[1,2])
        self.assertEquals(resolve(url).func, remove_label)

class TestCommentUrls(SimpleTestCase):

    def test_new_comment_url_resolves(self):
        url = reverse('new_comment', args=['1'])
        self.assertEquals(resolve(url).func, create_update_comment)
        
    def test_edit_comment_url_resolves(self):
        url = reverse('edit_comment', args=['1', '2'])
        self.assertEquals(resolve(url).func, create_update_comment)
    
    def test_delete_comment_url_resolves(self):
        url = reverse('delete_comment', args=['1', '2'])
        self.assertEquals(resolve(url).func, comment_delete_view)
    
    def test_one_comment_url_resolves(self):
        url = reverse('one_comment', args=['2'])
        self.assertEquals(resolve(url).func.view_class, OneCommentView)

class TestIssuesUrls(SimpleTestCase):

    def test_create_issue_url(self):
        url=reverse('new_issue', args=[1])
        self.assertEquals(resolve(url).func, create_update_issue)

    def test_edit_issue_url(self):
        url=reverse('edit_issue', args=[1, 1])
        self.assertEquals(resolve(url).func, create_update_issue)

    def test_delete_isse_url(self):
        url=reverse('delete_issue', args=[1])
        self.assertEquals(resolve(url).func.view_class, IssueDelete)
