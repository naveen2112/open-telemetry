"""
Django view for rendering the errors
"""
from django.shortcuts import redirect, render


def home(request):
    """
    Redirects the user to the 'induction-kit' page
    """
    return redirect("induction-kit")


def error_404(request, exception):
    """
    Handles the 404 error (page not found)
    """
    return render(request, "induction_kit.html")


def error_500(request):
    """
    Handles the 500 error (internal server error)
    """
    return render(request, "induction_kit.html")
