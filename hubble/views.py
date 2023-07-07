import logging

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from core import constants
from hubble import auth_helper
from hubble.models import User
from hubble_report import settings
from hubble_report.settings import ENV_NAME


# To make sure correct authentication method is renderred
def login(request):
    context = {}
    context[
        "login_method"
    ] = ENV_NAME  # This context variable will be used in template to render correct authentication method
    context["ENVIRONMENT_DEVELOPMENT"] = constants.ENVIRONMENT_DEVELOPMENT
    return render(request, "auth/login.html", context)


# Authenticates the user
def signin(request):
    if (
        ENV_NAME == constants.ENVIRONMENT_DEVELOPMENT
    ):  # To ensure the authentication method
        if request.method == "POST":
            user_email = request.POST.get("email")
            if User.objects.filter(email=user_email).exists():
                user = User.objects.get(email=user_email)
                if user is not None:
                    auth_login(request, user)
                    return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    " %s is an invalid mail-id, please enter a valid mail-id."
                    % user_email,
                )
                return redirect("login")
        else:
            return redirect("login")
    else:
        flow = auth_helper.get_sign_in_flow(request.get_host())
        try:
            request.session["auth_flow"] = flow
        except Exception as e:
            print(e)
            logging.error(f"An error has been occured while login {e}")
        return HttpResponseRedirect(flow["auth_uri"])


# Logout feature
def signout(request):
    auth_helper.remove_user_and_token(request)
    logout(request)
    return HttpResponseRedirect(reverse("login"))


# Redirects to Microsoft SSO
def callback(request):
    result = auth_helper.get_token_from_code(request)
    data = result["id_token_claims"]
    user_crendentials = data["preferred_username"]
    try:
        user = User.objects.get(email=user_crendentials)
    except Exception as e:
        user = None
    if (
        user is not None
    ):  # Checks whether the authenticated member is form Mallow or no, by checking with Database
        auth_login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        messages.add_message(
            request,
            messages.ERROR,
            " %s is an invalid mail-id, please enter a valid mail-id."
            % user_crendentials,
        )
        return redirect("login")


def health_check(request):
    return JsonResponse(data="", status=200, safe=False)


def error_404(request, exception=None):
    return render(request, "errors/404.html")