import json

import requests
from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter as BaseExceptionReporter

from hubble_report.settings import env


class ExceptionReporter(BaseExceptionReporter):
    def get_traceback_data(self):
        data = super().get_traceback_data()

        # Remove sensitive data from the report
        if "settings" in data:
            del data["settings"]

        if "request_meta" in data:
            del data["request_meta"]

        return data


class TeamsExceptionHandler(AdminEmailHandler):
    def emit(self, record, *args, **kwargs):
        url = env("TEAMS_LOGGING_WEBHOOK_URL")

        if url:
            try:
                request = record.request
                subject = "%s (%s IP): %s" % (
                    record.levelname,
                    (
                        "internal"
                        if request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
                        else "EXTERNAL"
                    ),
                    record.getMessage(),
                )
            except Exception:
                subject = "%s: %s" % (record.levelname, record.getMessage())
                request = None
            subject = self.format_subject(subject)

            if record.exc_info:
                exc_info = record.exc_info
            else:
                exc_info = (None, record.getMessage(), None)

            reporter = ExceptionReporter(request, is_email=False, *exc_info)

            message = reporter.get_traceback_text()

            headers = {"Content-Type": "application/json"}

            COLOR_CODES = {
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
                "themeColor": COLOR_CODES.get(record.levelname, "#00e07f"),
                "sections": [
                    {
                        "title": subject,
                        "activitySubtitle": "Admins, pay attention please!",
                        "facts": [
                            {"name": "Level:", "value": record.levelname},
                            {
                                "name": "Method:",
                                "value": request.method if request else "No Request",
                            },
                            {
                                "name": "Path:",
                                "value": request.path if request else 'No Request'
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
                            {"name": "Exception Details:", "value": message},
                        ],
                    }
                ],
            }

            requests.post(url, headers=headers, data=json.dumps(data))
