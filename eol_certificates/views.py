# Installed packages (via pip)
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.utils.translation import ugettext as _
from django.views.generic.base import View

# Edx dependencies
from lms.djangoapps.certificates.models import GeneratedCertificate

class EolValidateCertificatesView(View):
    """
    Allows you to check if an specific uuid has a certificate
    """
    def get(self, request):
        context = {
            "csrftoken": csrf(request)["csrf_token"]
        }
        return render(request,'eol_certificates/validate_certificates.html', context)
    
    def post(self, request):
        context = {
            "exists": False,
            "csrftoken": csrf(request)["csrf_token"]
        }
        # Validate user form data
        validation = self.validate_data(request.POST)
        cert_id = request.POST.get('cert-id')
        # If data is invalid, send error flag and form data
        if validation['error']:
            context['error'] = validation['error_attr']
            context['_id'] = request.POST.get('cert-id')
            return render(request, 'eol_certificates/validate_certificates.html', context)
        else:
            context['success'] = True
            return redirect('/certificates/' + cert_id)

    def validate_data(self, data):
        """
        Validate all form data
        """
        if not GeneratedCertificate.objects.filter(
                verify_uuid=data['cert-id']
            ).exists():
            return {
                'error': True,
                'error_attr': _('Certificate was not found')
            }
        return {
            'error': False
        }
