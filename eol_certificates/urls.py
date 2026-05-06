# Installed packages (via pip)
from django.conf.urls import url

# Internal project dependencies
from .views import EolValidateCertificatesView

urlpatterns = [
    url(r'certificates/validate$', EolValidateCertificatesView.as_view(), name='validate_certificate_view'),
]
