from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.models import modelform_factory
from django.test import Client, TestCase
from django.utils.translation import deactivate_all, override

from .models import CustomLanguagesModel, SpecificModel, TestModel


class Test(TestCase):
    def setUp(self):
        deactivate_all()

    def login(self):
        self.user = User.objects.create_superuser(
            'admin', 'admin@test.ch', 'blabla')
        client = Client()
        client.force_login(self.user)
        return client

    def test_meta(self):
        self.assertEqual(
            [f.name for f in TestModel._meta.get_fields()],
            ['id', 'name_en', 'name_de', 'other_en', 'other_de'],
        )

        creation_counters = [
            TestModel._meta.get_field(field).creation_counter
            for field in ['name_en', 'name_de', 'other_en', 'other_de']
        ]
        self.assertEqual(
            creation_counters,
            sorted(creation_counters),
        )

    def test_form_field_order(self):
        form = modelform_factory(TestModel, fields='__all__')()
        self.assertEqual(
            list(form.fields),
            ['name_en', 'name_de', 'other_en', 'other_de'],
        )

    def test_translated_attributes(self):
        m = TestModel()
        with override('en'):
            self.assertEqual(m.stuff, m.stuff_en)
        with override('de'):
            self.assertEqual(m.stuff, m.stuff_de)
        with override('bla'):
            self.assertRaises(AttributeError, lambda: m.stuff)

    def test_admin(self):
        client = self.login()
        response = client.get('/admin/testapp/testmodel/add/')
        self.assertContains(
            response,
            'Name [de]',
        )
        self.assertContains(
            response,
            'Other [en]',
        )

    def test_custom_languages(self):
        m = CustomLanguagesModel()

        self.assertEqual(m.name, 'NO VALUE')
        m.name_it = 'it'
        self.assertEqual(m.name, 'it')
        m.name_fr = 'fr'
        self.assertEqual(m.name, 'fr')
        m.name_it = ''
        self.assertEqual(m.name, 'fr')

        # The attributes from LANGUAGES should not exist:
        with self.assertRaises(AttributeError):
            m.name_en
        with self.assertRaises(AttributeError):
            m.name_de

    def test_translated_field_instance(self):
        self.assertEqual(
            CustomLanguagesModel.name._languages,
            ('fr', 'it'),
        )
        m = CustomLanguagesModel()
        with self.assertRaises(AttributeError):
            m.name._languages

        self.assertEqual(
            m.__class__.name._languages,
            ('fr', 'it'),
        )

    def test_specific(self):
        m = SpecificModel()

        with self.assertRaises(ValidationError) as cm:
            m.full_clean()

        self.assertEqual(
            list(cm.exception.error_dict),
            ['name_en'],
        )

        m.name_en = 'bla'
        m.full_clean()
