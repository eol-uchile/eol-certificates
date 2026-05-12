# Installed packages (via pip)
from django.conf.urls import url

# Internal project dependencies
from .views import EolValidateCertificatesView, EolReportCertificateView

urlpatterns = [
    url(r'certificates/validate$', EolValidateCertificatesView.as_view(), name='validate_certificate_view'),
    url(r'reports/issued_certificates', EolReportCertificateView.as_view(), name='issued_certificates'),
]
