from django.http import HttpResponseForbidden


class VerifiedUser:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_employed:
            return HttpResponseForbidden()
        return self.get_response(request)
