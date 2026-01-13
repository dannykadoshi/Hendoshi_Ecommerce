from django.shortcuts import render

def index(request):
    """
    View to return the homepage
    """
    return render(request, 'home/index.html')