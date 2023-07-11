"""
Microsoft teams log configuration for the exception occured in the application
"""
import json

import requests
from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter as BaseExceptionReporter

from hubble_report.settings import env


class ExceptionReporter(BaseExceptionReporter):
    """
    Custom exception reporter that retrieves traceback data and
    removes sensitive information
    """

    def get_traceback_data(self):
        data = super().get_traceback_data()

        # Remove sensitive data from the report
        if "settings" in data:
            del data["settings"]

        if "request_meta" in data:
            del data["request_meta"]

        return data


class TeamsExceptionHandler(AdminEmailHandler):
    """
    Custom exception handler that sends exception details to Microsoft Teams.

    Inherits from the AdminEmailHandler class
    """

    def emit(self, record):
        url = env("TEAMS_LOGGING_WEBHOOK_URL")

        if url:
            try:
                request = record.request
                subject = f"{record.levelname}\
                    ({'internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS else 'EXTERNAL'} IP): \
                    {record.getMessage()}"
            except Exception:
                subject = f"{record.levelname}: {record.getMessage()}"
                request = None
            subject = self.format_subject(subject)

            if record.exc_info:
                exc_info = record.exc_info
            else:
                exc_info = (None, record.getMessage(), None)

            reporter = ExceptionReporter(
                request, is_email=False, *exc_info
            )

            message = reporter.get_traceback_text()

            headers = {"Content-Type": "application/json"}

            COLOR_CODES = {  # pylint: disable=invalid-name
                "DEBUG": "#808080",
                "INFO": "#00e07f",
                "WARNING": "#FFFF00",
                "ERROR": "#FF0000",
                "CRITICAL": "#800000",
            }

            data = {
                "summary": subject,
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "themeColor": COLOR_CODES.get(
                    record.levelname, "#00e07f"
                ),
                "sections": [
                    {
                        "title": subject,
                        "activitySubtitle": "Admins, pay attention please!",
                        "facts": [
                            {
                                "name": "Level:",
                                "value": record.levelname,
                            },
                            {
                                "name": "Method:",
                                "value": request.method
                                if request
                                else "No Request",
                            },
                            {
                                "name": "Path:",
                                "value": request.path
                                if request
                                else "No Request",
                            },
                            {
                                "name": "Status Code:",
                                "value": record.status_code
                                if hasattr(record, "status_code")
                                else "None",
                            },
                            {
                                "name": "UA:",
                                "value": (
                                    request.META["HTTP_USER_AGENT"]
                                    if request and request.META
                                    else "No Request"
                                ),
                            },
                            {
                                "name": "GET Params:",
                                "value": json.dumps(request.GET)
                                if request
                                else "No Request",
                            },
                            {
                                "name": "POST Data:",
                                "value": json.dumps(request.POST)
                                if request
                                else "No Request",
                            },
                            {
                                "name": "Exception Details:",
                                "value": message,
                            },
                        ],
                    }
                ],
            }

            requests.post(
                url, headers=headers, data=json.dumps(data), timeout=10
            )
