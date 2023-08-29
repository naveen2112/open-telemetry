from django.http import HttpResponseForbidden
from core.constants import PROBATIONER_EMAILS


class VerifiedUser:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_employed
            and not request.user.email in PROBATIONER_EMAILS
        ):
            return HttpResponseForbidden()
        return self.get_response(request)
