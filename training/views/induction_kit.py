import os
from django.conf import settings
from django.views.generic import TemplateView
from django.http import FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

class InductionKit(LoginRequiredMixin, TemplateView):
    """
    Induction Kit
    """
    template_name = "induction_kit.html"
    # Getting the list of pdf files in the static folder.
    static_path = list(settings.STATICFILES_DIRS)
    extra_context = {
        "pdf_files": [file for file in os.listdir(f"{static_path[0]}/training/pdf") if os.path.splitext(file)[1] == ".pdf"
        ],
    }


@login_required()
def induction_kit_detail(request, text):
    """
    Induction Kit Detail
    """
    static_path = list(settings.STATICFILES_DIRS)
    file_path = f"{static_path[0]}/training/pdf/{text}"
    return FileResponse(open(file_path, "rb"), content_type="application/pdf")