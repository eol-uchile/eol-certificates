# Installed packages (via pip)
from django.conf.urls import url

# Internal project dependencies
from .views import validate_certificate

urlpatterns = [
    url(r'certificates/validate$', validate_certificate, name='validate_certificate'),
]
