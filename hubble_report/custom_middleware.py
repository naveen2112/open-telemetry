
from hubble_report.urls import include_subdomain_urls

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        include_subdomain_urls(request.get_host().split('.')[0])
        response = self.get_response(request)
        return response
