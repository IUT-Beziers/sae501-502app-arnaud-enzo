from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'dashboard/index.html')

def home(request):
    return render(request, 'dashboard/home.html')

def agent(request):
    return render(request, 'dashboard/agent.html')

def settings(request):
    return render(request, 'dashboard/settings.html')