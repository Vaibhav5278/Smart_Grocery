from django.http import HttpResponse
from django.shortcuts import render

def index(request):

    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def add_item(request):
    return render(request,'add_item.html')

def login(request):
    return render(request,'login.html')

def profile(request):
    return render(request,'profile.html')

def register(request):
    return render(request,'register.html')

def view_item(request):
    return render(request,'view_item.html')

def report(request):
    return render(request,'report.html')

def mark_wasted(request):
    return render(request,'mark_wasted.html')

def waste_logged(request):
    return render(request,'waste_logged.html')

def functionality(request):
    return render(request,'functionality.html')

def how_it_works(request):
    return render(request,'how_it_works.html')



