from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from hubble.auth_helper import get_sign_in_flow, get_token_from_code, remove_user_and_token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from hubble.models import Users
from django.contrib.auth import login, logout
from hubble_report.settings import DEVELOP


dev = int(DEVELOP)

def index(request):
    if dev == 1:
        return render(request, 'auth/dev_login.html')
    else:
        context = initialize_context(request)
        return render(request, 'auth/login.html', context)

def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error == None:
      context['errors'] = []
    context['errors'].append(error)
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context

@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'layouts/base.html')

def sign_in(request):
    if dev == 1:
        if request.method == 'POST':
            user_email = request.POST.get('email')
            user = Users.objects.get(email=user_email)
            if user.name is not None:
                login(request, user)
                return redirect('/dash/')            
            else:
                error_message = "Invalid email address."
                return render(request, 'auth/dev_login.html', {'error_message': error_message})
        else:
            return render(request, 'auth/dev_login.html')
    else:
        flow = get_sign_in_flow()
        try:
            request.session['auth_flow'] = flow
        except Exception as e:
            print(e)
        return HttpResponseRedirect(flow['auth_uri'])

def sign_out(request):
    remove_user_and_token(request)
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def callback(request):
    result = get_token_from_code(request)
    data = result['id_token_claims']
    user_crendentials = data['preferred_username']
    user = Users.objects.get(email = user_crendentials)
    if user is not None:
        login(request, user)
        return redirect('/dash/')
    else:
        error_message = "Invalid email address."
        return render(request, 'auth/dev_login.html', {'error_message': error_message})
