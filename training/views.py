import os
from django.conf import settings
from django.views.generic import TemplateView


class InductionKit(TemplateView):
    template_name = "induction_kit.html"
    # Getting the list of pdf files in the static folder.
    static_folder_path = os.path.join(settings.BASE_DIR, "static/training/assets/pdf")
    pdf_files = [file for file in os.listdir(static_folder_path) if os.path.splitext(file)[1] == ".pdf"]

    extra_context = {
        "pdf_files": pdf_files,
    }


class InductionKitDetail(TemplateView):
    template_name = "kit_detail.html"
