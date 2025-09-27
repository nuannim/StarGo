from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def stars(request):
    return render(request, 'stars.html')

def stars_addnewstar(request):
    return render(request, 'stars_addnewstar.html')

def places(request):
    return render(request, 'places.html')

def places_addnewplace(request):
    return render(request, 'places_addnewplace.html')

def profile(request):
    return render(request, 'profile.html')

def profile_edit(request):
    return render(request, 'profile_edit.html')

def profile_changepassword(request):
    return render(request, 'profile_changepassword.html')

def profile_deleteaccount(request):
    return render(request, 'profile_deleteaccount.html')
