from django.shortcuts import redirect, render


def home(request):
    return redirect("induction-kit")


def error_404(request, exception):
    return render(request, "induction_kit.html")


def error_500(request):
    return render(request, "induction_kit.html")
