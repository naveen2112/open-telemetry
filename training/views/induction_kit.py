"""
Django view and a function for serving PDF files from a static folder, with 
authentication required for accessing the view
"""
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.views.generic import TemplateView


class InductionKit(LoginRequiredMixin, TemplateView):
    """
    Induction Kit
    """

    template_name = "induction_kit.html"
    # Getting the list of pdf files in the static folder.
    static_path = list(settings.STATICFILES_DIRS)
    extra_context = {
        "pdf_files": [
            file
            for file in os.listdir(f"{static_path[0]}/training/pdf")
            if os.path.splitext(file)[1] == ".pdf"
        ],
    }


@login_required()
def induction_kit_detail(request, text):  # pylint: disable=unused-argument
    """
    Induction Kit Detail
    """
    static_path = list(settings.STATICFILES_DIRS)
    file_path = f"{static_path[0]}/training/pdf/{text}"
    return FileResponse(open(file_path, "rb"), content_type="application/pdf")
