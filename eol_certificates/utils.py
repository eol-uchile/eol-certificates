#!/usr/bin/env python
# -- coding: utf-8 --
# Python Standard Libraries
from datetime import datetime
from functools import partial
from time import time
import codecs
import csv
import logging

# Installed packages (via pip)
from celery import task
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.translation import ugettext_noop
from eol_sso.services.interface import get_user_id_with_indiv_id_list
from pytz import UTC
import six

# Edx dependencies
from common.djangoapps.util.file import course_filename_prefix_generator
from lms.djangoapps.instructor_task.api_helper import submit_task
from lms.djangoapps.instructor_task.models import ReportStore
from lms.djangoapps.instructor_task.tasks_base import BaseInstructorTask
from lms.djangoapps.instructor_task.tasks_helper.runner import run_main_task, TaskProgress
from opaque_keys.edx.keys import CourseKey

logger = logging.getLogger(__name__)

@task(base=BaseInstructorTask, queue='edx.lms.core.low')
def process_data(entry_id, xmodule_instance_args):
    action_name = ugettext_noop('generated')
    task_fn = partial(task_get_data, xmodule_instance_args)
    return run_main_task(entry_id, task_fn, action_name)

def task_get_data(
        _xmodule_instance_args,
        _entry_id,
        course_id,
        task_input,
        action_name):

    base_url = task_input['base_url']
    start_time = time()
    start_date = datetime.now(UTC)
    num_reports = 1
    task_progress = TaskProgress(action_name, num_reports, start_time)
    current_step = {'step': 'EolReportCertificate - Getting users data'}
    task_progress.update_task_state(extra_meta=current_step)

    students = get_all_enrolled_users(course_id, base_url)

    report_store = ReportStore.from_config('GRADES_DOWNLOAD')
    csv_name = 'Reporte_de_Certificados_Emitidos'

    report_name = u"{course_prefix}_{csv_name}_{timestamp_str}.csv".format(
        course_prefix=course_filename_prefix_generator(course_id),
        csv_name=csv_name,
        timestamp_str=start_date.strftime("%Y-%m-%d-%H%M")
    )
    output_buffer = ContentFile('')
    if six.PY2:
        output_buffer.write(codecs.BOM_UTF8)
    csvwriter = csv.writer(output_buffer)

    header = ['Username', 'Run', 'Email', 'Modo', 'Url']
    csvwriter.writerow(_get_utf8_encoded_row(header))
    csvwriter.writerows(ReportStore()._get_utf8_encoded_rows(students))

    current_step = {'step': 'EolReportCertificate - Uploading CSV'}
    task_progress.update_task_state(extra_meta=current_step)

    output_buffer.seek(0)
    report_store.store(course_id, report_name, output_buffer)
    current_step = {
        'step': 'EolReportCertificate - CSV uploaded',
        'report_name': report_name,
    }

    return task_progress.update_task_state(extra_meta=current_step)

def task_process_data(request, course_id):
    course_key = CourseKey.from_string(course_id)
    task_type = 'EOL_REPORT_CERTIFICATE'
    task_class = process_data
    task_input = {'base_url': request.build_absolute_uri('/')[0:-1]}
    task_key = "EOL_REPORT_CERTIFICATE_{}".format(course_id)

    return submit_task(
        request,
        task_type,
        task_class,
        course_key,
        task_input,
        task_key)


def _get_utf8_encoded_row(row):
    """
    Given a list of `rows` containing unicode strings, return a
    new list of rows with those strings encoded as utf-8 for CSV
    compatibility.
    """
    
    if six.PY2:
        return [six.text_type(item).encode('utf-8') for item in row]
    else:
        return [six.text_type(item) for item in row]

def get_all_enrolled_users(course_key, base_url):
        """
        Get all enrolled student with Issued Certificates for course_key.
        """
        students = []
        enrolled_students = User.objects.filter(
            generatedcertificate__status='downloadable',
            generatedcertificate__course_id=course_key
        ).order_by('username').values('id', 'username', 'email', 'generatedcertificate__verify_uuid', 'generatedcertificate__mode')
        user_id_list = enrolled_students.values_list('id', flat=True)
        user_indiv_id_list = get_user_id_with_indiv_id_list(user_id_list)
        user_indiv_id_dict = {id: indiv_id for id, indiv_id in user_indiv_id_list}
        for user in enrolled_students:
            user['indiv_id'] = user_indiv_id_dict.get(user['id'], '')
            students.append([
                user['username'],                
                user['indiv_id'],
                user['email'],
                user['generatedcertificate__mode'],
                '{}{}'.format(base_url, reverse('certificates:render_cert_by_uuid', kwargs={'certificate_uuid':user['generatedcertificate__verify_uuid']}))])
        return students
    