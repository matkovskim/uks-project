from django.test import SimpleTestCase
from uks_app.forms import MilestoneForm, LabelForm

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