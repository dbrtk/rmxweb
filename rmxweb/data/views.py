
from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return HttpResponse('This is the home of the "data" app.')
