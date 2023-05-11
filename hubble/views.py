from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from hubble_report.settings import ENV_NAME
from django.http import HttpResponseRedirect
from hubble import auth_helper
from hubble.models import User
from core import constants
from django.http import JsonResponse


def index(request):
    context = {}
    if ENV_NAME == constants.ENVIRONMENT_DEVELOPMENT:
        context["login_method"] = "testing"
    else:
        context["login_method"] = "production"
    return render(request, "auth/login.html", context)


def signin(request):
    if ENV_NAME == constants.ENVIRONMENT_DEVELOPMENT:
        if request.method == "POST":
            user_email = request.POST.get("email")
            if User.objects.filter(email=user_email).exists():
                user = User.objects.get(email=user_email)
                if user is not None:
                    login(request, user)
                    return redirect("index")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    " %s is an invalid mail-id, please enter a valid mail-id."
                    % user_email,
                )
                return redirect("index")
        else:
            return redirect("index")
    else:
        flow = auth_helper.get_sign_in_flow()
        try:
            request.session["auth_flow"] = flow
        except Exception as e:
            print(e)
        return HttpResponseRedirect(flow["auth_uri"])


def signout(request):
    auth_helper.remove_user_and_token(request)
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def callback(request):
    result = auth_helper.get_token_from_code(request)
    data = result["id_token_claims"]
    user_crendentials = data["preferred_username"]
    user = User.objects.get(email=user_crendentials)
    if user is not None:
        login(request, user)
        return redirect("index")
    else:
        messages.add_message(
            request,
            messages.ERROR,
            " %s is an invalid mail-id, please enter a valid mail-id."
            % user_crendentials,
        )
        return redirect("index")
    

def health_check(request):
    return JsonResponse(data="", status=200, safe=False)