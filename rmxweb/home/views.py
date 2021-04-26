from django.shortcuts import HttpResponse

# Create your views here.


def home(request):

    return HttpResponse('This is the home page of proximity-bot.')
