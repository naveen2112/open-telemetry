from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def report(request):
    context = {}
    return render(
        request=request,
        template_name="reports.html",
        context=context,
    )