from django.test import SimpleTestCase
from django.urls import reverse, resolve
from uks_app.views import create_update_issue, IssueDelete, OneIssueView

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