class SubdomainClassifier:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        request.subdomain = (request.get_host().split(".")[0]).split("-")[0] # Get the sub-domain from request
        if request.subdomain == "training" or request.subdomain == "reports": 
            request.urlconf = request.subdomain + ".urls"
        return self.get_response(request)
