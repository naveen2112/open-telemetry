class SubdomainClassifier:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        request.subdomain = request.get_host().split(".")[0]
        request.urlconf = request.subdomain + ".urls"
        return self.get_response(request)

