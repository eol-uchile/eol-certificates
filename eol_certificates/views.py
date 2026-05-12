#!/usr/bin/env python
# -- coding: utf-8 --
# Python Standard Libraries
import logging

# Installed packages (via pip)
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.utils.translation import ugettext as _
from django.views.generic.base import View

# Edx dependencies
from lms.djangoapps.certificates.models import GeneratedCertificate
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.instructor import permissions
from lms.djangoapps.instructor_task.api_helper import AlreadyRunningError
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

# Internal project dependencies
from .utils import task_process_data

logger = logging.getLogger(__name__)

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

class EolReportCertificateView(View):
    """
    Return a csv of Issued Certificates.
    """
    @transaction.non_atomic_requests
    def dispatch(self, args, **kwargs):
        return super(EolReportCertificateView, self).dispatch(args, **kwargs)

    def get(self, request, **kwargs):
        if not request.user.is_anonymous:
            course_id = request.GET.get('course', "")
            data_error = self.validate_data(request.user, course_id)
            if len(data_error) == 0:
                return self.get_data_report(request, course_id)
            else:
                data_error['status'] = 'Error'
                return JsonResponse(data_error)
        else:
            logger.error("EolReportCertificate - User is Anonymous")
        raise Http404()

    def get_data_report(self, request, course_id):
        """
        Generate report with task_process.
        """
        try:
            task = task_process_data(request, course_id)
            success_status = 'Generating'
            return JsonResponse({"status": success_status, "task_id": task.task_id})
        except AlreadyRunningError:
            logger.error("EolReportCertificate - Task Already Running Error, user: {}, course_id: {}".format(request.user, course_id))
            return JsonResponse({'status': 'AlreadyRunningError'})

    def validate_data(self, user, course_id):
        """
        Validates the course_id and the user permissions.
        """
        error = {}
        if course_id == "":
            logger.error("EolReportCertificate - Empty course, user: {}".format(user.id))
            error['empty_course'] = True
        else:
            if not self.validate_course(course_id):
                logger.error("EolReportCertificate - Course doesn't exists, user: {}, course_id: {}".format(user.id, course_id))
                error['error_curso'] = True
            else:
                if not self.user_have_permission(user, course_id):
                    logger.error("EolReportCertificate - User doesn't have permission in the course, course: {}, user: {}".format(course_id, user))
                    error['user_permission'] = True
        return error
    
    def validate_course(self, course_id):
        """
        Verify if course_id exists.
        """
        try:
            aux = CourseKey.from_string(course_id)
            return CourseOverview.objects.filter(id=aux).exists()
        except InvalidKeyError:
            return False

    def user_have_permission(self, user, course_id):
        """
        Verify if user is instructor, staff_course, data researcher or superuser.
        """
        course_key = CourseKey.from_string(course_id)
        return self.is_instructor_or_staff(user, course_key) or user.is_staff

    def is_instructor_or_staff(self, user, course_key):
        """
        Verify if the user is instructor, staff course or data researcher.
        """
        try:
            course = get_course_with_access(user, "load", course_key)
            data_researcher_access = user.has_perm(permissions.CAN_RESEARCH, course_key)
            return bool(has_access(user, 'instructor', course)) or bool(has_access(user, 'staff', course)) or data_researcher_access
        except Exception as e:
            logger.error('EolReportCertificate - Error in is_instructor_or_staff({}, {}), Exception {}'.format(user, str(course_key), str(e)))
            return False
