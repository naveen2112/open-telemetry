from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def health_check(request):
    return JsonResponse(data="", status=200, safe=False)