# -*- coding: utf-8 -*-


from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginSettings, PluginURLs, ProjectType, SettingsType


class EolCertificateConfig(AppConfig):
    name = 'eol_certificates'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: '',
                PluginURLs.REGEX: r'^',
                PluginURLs.RELATIVE_PATH: 'urls',
            }},
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: 'settings.common'},
            },
        }}

    def ready(self):
        pass
