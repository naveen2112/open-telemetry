from django.shortcuts import render


def index(request):
    context = {}
    return render(
        request=request,
        template_name="training.html",
        context=context,
    )
