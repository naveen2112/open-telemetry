"""
Django view for rendering the errors
"""
from django.shortcuts import redirect, render


# It is used to ommit 'unused-argument'.The function has unused arguments
def home(request):  # pylint: disable=unused-argument
    """
    Redirects the user to the 'induction-kit' page
    """
    return redirect("induction-kit")


# It is used to ommit 'unused-argument'.The function has unused arguments
def error_404(request, exception):  # pylint: disable=unused-argument
    """
    Handles the 404 error (page not found)
    """
    return render(request, "errors/404.html", status=404)


def error_500(request):  # pragma: no cover
    """
    Handles the 500 error (internal server error)
    """
    return render(request, "errors/500.html", status=500)
