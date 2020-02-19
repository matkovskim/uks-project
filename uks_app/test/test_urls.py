from django.test import SimpleTestCase
from django.urls import reverse, resolve
from uks_app.views import create_update_milestone, OneMilestoneView, MilestoneDelete, create_label, remove_label

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

class TestLabelUrls(SimpleTestCase):
    
    def test_list_url_is_resolves(self):
        url = reverse('new_label', args=[1])
        self.assertEquals(resolve(url).func, create_label)


    def test_remove_label_url_resolves(self):
        url = reverse('remove_label', args=[1,2])
        self.assertEquals(resolve(url).func, remove_label)