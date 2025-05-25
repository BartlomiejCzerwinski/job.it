from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def match(request):
    return JsonResponse({
        'message': 'Hello from Matching App!'
    })
