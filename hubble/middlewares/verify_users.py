"""
Verified User Middleware

This middleware class is responsible for verifying the user's
authentication and employment status.
"""
from django.http import HttpResponseForbidden


class VerifiedUser:
    """
    Middleware class for verifying the user's authentication and employment status.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Verifies the user's authentication and employment status
        """
        if (
            request.user.is_authenticated
            and not request.user.is_employed
        ):
            return HttpResponseForbidden()
        return self.get_response(request)
