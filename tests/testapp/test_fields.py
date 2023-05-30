import re
from unittest import skipIf

import django
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.forms.models import modelform_factory
from django.test import Client, TestCase
from django.utils.translation import deactivate_all, override

from testapp.models import (
    CustomLanguagesModel,
    ListDisplayModel,
    ModelWithAnyFallback,
    ModelWithFallback,
    SpecificModel,
    TestModel,
)
from translated_fields.utils import language_code_formfield_callback


class Test(TestCase):
    def setUp(self):
        deactivate_all()

    def login(self):
        self.user = User.objects.create_superuser("admin", "admin@test.ch", "blabla")
        client = Client()
        client.force_login(self.user)
        return client

    def test_meta(self):
        self.assertEqual(
            [f.name for f in TestModel._meta.get_fields()],
            ["id", "name_en", "name_de", "other_en", "other_de"],
        )

        creation_counters = [
            TestModel._meta.get_field(field).creation_counter
            for field in ["name_en", "name_de", "other_en", "other_de"]
        ]
        self.assertEqual(creation_counters, sorted(creation_counters))

        other_en = TestModel._meta.get_field("other_en")
        other_de = TestModel._meta.get_field("other_de")

        with override("en"):
            self.assertEqual(str(other_en.verbose_name), "other field")
            self.assertEqual(str(other_de.verbose_name), "other field")

        with override("de"):
            self.assertEqual(str(other_en.verbose_name), "anderes Feld")
            self.assertEqual(str(other_de.verbose_name), "anderes Feld")

    def test_form_field_order(self):
        form = modelform_factory(TestModel, fields="__all__")()
        self.assertEqual(
            list(form.fields), ["name_en", "name_de", "other_en", "other_de"]
        )

    def test_translated_fields(self):
        m = TestModel()
        with override(None):
            self.assertEqual(m.name, m.name_en)
        with override("en"):
            self.assertEqual(m.name, m.name_en)
        with override("de"):
            self.assertEqual(m.name, m.name_de)
        with override("bla"):
            self.assertRaises(AttributeError, lambda: m.name)

    def test_translated_attributes(self):
        m = TestModel()
        with override(None):
            self.assertEqual(m.stuff, m.stuff_en)
        with override("en"):
            self.assertEqual(m.stuff, m.stuff_en)
        with override("de"):
            self.assertEqual(m.stuff, m.stuff_de)
        with override("bla"):
            self.assertRaises(AttributeError, lambda: m.stuff)

    def test_translated_attributes_with_fallback_to_default(self):
        m = TestModel()
        with override("de"):
            self.assertEqual(m.attr_default, "en")

    def test_translated_attributes_with_fallback_to_any(self):
        m = TestModel()
        with override("de"):
            self.assertEqual(m.attr_any, "en")

    def test_admin_changelist_redirect(self):
        """Redirects have no render() method, TranslatedFieldAdmin shouldn't crash"""
        client = self.login()
        response = client.get("/admin/testapp/testmodel/?hello=world")
        self.assertRedirects(response, "/admin/testapp/testmodel/?e=1")

    def test_admin(self):
        client = self.login()
        response = client.get("/admin/testapp/testmodel/add/")
        self.assertContains(response, "Name [de]")
        self.assertContains(response, "Other field [en]")

        m = TestModel.objects.create(name_en="Test")

        response = client.get("/admin/testapp/testmodel/")
        self.assertContains(response, "<span>Name</span>")
        self.assertContains(response, "<span>Other field</span>")

        self.assertContains(response, "Name [en]</a>")
        self.assertContains(response, "Name [de]</a>")

        self.assertContains(
            response,
            '<th class="field-name_en"><a'
            ' href="/admin/testapp/testmodel/{}/change/">Test</a></th>'.format(m.id),
            html=True,
        )
        self.assertContains(response, 'id="id_form-0-name_de"')

        response = client.get(f"/admin/testapp/testmodel/{m.id}/change/")
        self.assertContains(
            response,
            '<label>Other field [en]:</label><div class="readonly"></div>',
            html=True,
        )

        response = client.post(
            "/admin/testapp/testmodel/add/", {"name_en": "Test", "name_de": "Test"}
        )
        self.assertRedirects(response, "/admin/testapp/testmodel/")

        # print(response, response.content.decode("utf-8"))

    def test_custom_languages(self):
        m = CustomLanguagesModel()

        self.assertEqual(m.name, "NO VALUE")
        m.name_it = "it"
        self.assertEqual(m.name, "it")
        m.name_fr = "fr"
        self.assertEqual(m.name, "fr")
        m.name_it = ""
        self.assertEqual(m.name, "fr")

        # The attributes from LANGUAGES should not exist:
        with self.assertRaises(AttributeError):
            _read = m.name_en
        with self.assertRaises(AttributeError):
            _read = m.name_de

    def test_translated_field_instance(self):
        self.assertEqual(CustomLanguagesModel.name.languages, ["fr", "it"])
        m = CustomLanguagesModel()
        with self.assertRaises(AttributeError):
            _read = m.name.languages

        self.assertEqual(m.__class__.name.languages, ["fr", "it"])

        self.assertEqual(CustomLanguagesModel.name.fields, ["name_fr", "name_it"])

        # Not str, lazy!
        self.assertFalse(CustomLanguagesModel.name.short_description is str)

    def test_specific(self):
        m = SpecificModel()

        with self.assertRaises(ValidationError) as cm:
            m.full_clean()

        self.assertEqual(list(cm.exception.error_dict), ["name_en"])

        m.name_en = "bla"
        m.full_clean()

        self.assertEqual(str(m._meta.get_field("name_en").verbose_name), "name")
        self.assertEqual(str(m._meta.get_field("name_de").verbose_name), "Der Name")

    def test_setter(self):
        m = TestModel()
        with override("en"):
            m.name = "english"
        with override("de"):
            m.name = "german"
        self.assertEqual(m.name_en, "english")
        self.assertEqual(m.name_de, "german")

        # I would rather not write code that prevents this...
        with override("bla"):
            m.name = "blub"
        self.assertEqual(m.name_bla, "blub")

    def test_list_display_columns(self):
        obj = ListDisplayModel.objects.create(
            name_en="english",
            name_de="german",
            choice_en="a",
            choice_de="b",
            is_active_de=False,
        )
        obj.file_en.save("test.txt", ContentFile(b"Hello"), save=True)

        client = self.login()
        response = client.get("/admin/testapp/listdisplaymodel/")

        # print(response.content.decode("utf-8"))

        self.assertContains(response, "<span>Stuff</span>")
        self.assertContains(response, "Name [en]")
        self.assertContains(response, "Name [de]")

        self.assertContains(response, "Andrew", 1)
        self.assertContains(response, "Betty", 1)

        self.assertContains(response, 'img src="/static/admin/img/icon-yes.svg"', 1)
        self.assertContains(response, 'img src="/static/admin/img/icon-no.svg"', 1)

        self.assertTrue(
            re.search(
                rb'<a href="/media/test(_\w+)?.txt">test(_\w+)?.txt</a>',
                response.content,
            )
        )

    def test_fallback(self):
        self.assertFalse(ModelWithFallback._meta.get_field("required_en").blank)
        self.assertTrue(ModelWithFallback._meta.get_field("required_de").blank)
        self.assertTrue(ModelWithFallback._meta.get_field("optional_en").blank)
        self.assertTrue(ModelWithFallback._meta.get_field("optional_de").blank)

        obj = ModelWithFallback(required_en="bla")
        with override("en"):
            self.assertEqual(obj.required, "bla")
        with override("de"):
            self.assertEqual(obj.required, "bla")
        with override(None):
            self.assertEqual(obj.required, "bla")

    def test_fallback_to_any(self):
        obj = ModelWithAnyFallback(optional_de="chic")
        with override("en"):
            self.assertEqual(obj.optional, "chic")
        with override("de"):
            self.assertEqual(obj.optional, "chic")

        obj.optional_en = "chic-en"
        with override("en"):
            self.assertEqual(obj.optional, "chic-en")
        with override("de"):
            self.assertEqual(obj.optional, "chic")

        obj = ModelWithAnyFallback()
        with override("en"):
            self.assertEqual(obj.optional, "")
        with override("de"):
            self.assertEqual(obj.optional, "")

    @skipIf(
        django.VERSION < (4, 2),
        "Specifying the callback wasn't officially supported before",
    )
    def test_formfield_callback(self):
        class Form(forms.ModelForm):
            class Meta:
                model = TestModel
                fields = "__all__"  # noqa: DJ007
                formfield_callback = language_code_formfield_callback

        with override("en"):
            result = str(Form())
            self.assertIn("Other field [en]:", result)
            self.assertIn("Other field [de]:", result)

        with override("de"):
            result = str(Form())
            self.assertIn("Anderes Feld [en]:", result)
            self.assertIn("Anderes Feld [de]:", result)
