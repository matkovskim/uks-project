from django.test import SimpleTestCase
from uks_app.forms import MilestoneForm, ProjectForm

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