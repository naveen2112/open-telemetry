from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from hubble.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token
from hubble.graph_helper import *
from django.contrib.auth.decorators import login_required

def index(request):
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

@login_required(login_url="/login/")
def dashboard(request):
    return render(request, 'layouts/base.html')

def sign_in(request):
    flow = get_sign_in_flow()
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    return HttpResponseRedirect(flow['auth_uri'])

def sign_out(request):
    remove_user_and_token(request)
    return HttpResponseRedirect(reverse('index'))

def callback(request):
    result = get_token_from_code(request)
    user = get_user(result['access_token']) 
    store_user(request, user)
    return render(request, 'layouts/base.html')
