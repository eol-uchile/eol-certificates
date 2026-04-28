# -*- coding: utf-8 -*-
# Installed packages (via pip)
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import ugettext as _
from mock import patch

# Edx dependencies
from common.djangoapps.student.tests.factories import UserFactory
from lms.djangoapps.certificates.models import GeneratedCertificate

class TestEolCertificate(TestCase):
    def setUp(self):
        with patch('common.djangoapps.student.models.cc.User.save'):
            # staff user
            self.user_staff = UserFactory(
                username='testuser3',
                password='12345',
                email='student2@edx.org',
                is_staff=True)
            self.client = Client()
        super(TestEolCertificate, self).setUp()

    def test_render_page(self):
        """
        Test render view GET function
        """
        url = reverse('eol_certificates:validate_certificate_view')
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)
    
    def test_view_validate_certificate(self):
        """
        Verify that the view redirects to the certificate detail page
        when a valid cert-id exists.
        """
        GeneratedCertificate.objects.create(verify_uuid='cert-id-test', user_id=self.user_staff.id)
        response  = self.client.post(
            reverse('eol_certificates:validate_certificate_view'),
            {'cert-id': 'cert-id-test'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/certificates/cert-id-test")
    
    def test_view_validate_certificate_no_valid_cert_id(self):
        """
        Ensure that providing an invalid cert-id does not trigger a redirect 
        and returns the appropriate response.
        1 cert-id empty
        2 cert-id not found
        """
        self.client.cookies.load({'openedx-language-preference': "es-419"})
        result  = self.client.post(
            reverse('eol_certificates:validate_certificate_view'),
            {'cert-id': ''}
        )
        self.assertEqual(result.status_code, 200)
        self.assertContains(result, _('Certificate was not found'))

        url = reverse('eol_certificates:validate_certificate_view')
        result  = self.client.post(url ,{'cert-id': 'fake-id'})
        self.assertEqual(result.status_code, 200)
        self.assertContains(result, _('Certificate was not found'))
