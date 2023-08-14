"""
Subdomain Classifier Middleware

This middleware class is responsible for classifying the subdomain of the 
incoming request and modifying the request accordingly.
"""
from hubble_report import settings


class SubdomainClassifier:
    """
    Middleware class for subdomain classification.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Classifies the subdomain of the incoming request and modifies the request accordingly.
        """
        request.subdomain = (request.get_host().split(".")[0]).split("-")[
            0
        ]  # Get the sub-domain from request
        if request.subdomain in ("training", "reports"):
            request.urlconf = request.subdomain + ".urls"
        settings.LOGIN_REDIRECT_URL = (
            "induction-kit" if request.subdomain == "training" else "index"
        )
        return self.get_response(request)
