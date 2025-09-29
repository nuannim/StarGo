from django.http import JsonResponse
from django.shortcuts import render
from .models import *
from django.db.models.functions import Concat
from django.db.models import Value

# Create your views here.
def index(request):
    return render(request, 'index.html')

# * ===== Stars Views ===========================
def stars(request):
    stars_queryset = Celebrities.objects.annotate(
        name=Concat('firstname', Value(' '), 'lastname')
    )

    star_data = list(stars_queryset.values(
        'id',
        'name',
    ))

    context = {
        'star_data': star_data
    }

    return render(request, 'stars.html', context)

def stars_addnewstar(request):
    return render(request, 'stars_addnewstar.html')

# def stars_sortby(request):
#     return render(request, 'stars_sortby.html')

def stars_sortby(request, celebrities_id):
    # * ก้อปมาจาก def stars()
    stars_queryset = Celebrities.objects.annotate(
        name=Concat('firstname', Value(' '), 'lastname')
    )

    star_data = list(stars_queryset.values(
        'id',
        'name',
    ))
    print(star_data)

    # * celebrities
    celebrities = Celebrities.objects.get(id=celebrities_id)

    wheretogo = Sightings.objects.filter(celebrities=celebrities_id).order_by('-arrivaldate')

    context = {
        'star_data': star_data,
        'celebrities': celebrities,
        'wheretogo': wheretogo,
    }


    return render(request, 'stars_sortby.html', context)

# * ===== Places Views =========================
def places(request):
    return render(request, 'places.html')

def places_addnewplace(request):
    return render(request, 'places_addnewplace.html')

def places_sortby(request):
    return render(request, 'places_sortby.html')

# * ===== Profile Views ========================
def profile(request):
    return render(request, 'profile.html')

def profile_edit(request):
    return render(request, 'profile_edit.html')

def profile_changepassword(request):
    return render(request, 'profile_changepassword.html')

def profile_deleteaccount(request):
    return render(request, 'profile_deleteaccount.html')

# * ===== other api (for js fetch) ========================
# def get_stars_data(request):
    # star = list(Celebrities.objects.values_list('firstname', flat=True))

    # star = list(Celebrities.objects.annotate(
    #     full_name=Concat('firstname', Value(' '), 'lastname')
    #     ).values_list('full_name', flat=True))

    # print(star)
    # return JsonResponse(star, safe=False)   
# =====
    # stars_queryset = Celebrities.objects.annotate(
    #     name=Concat('firstname', Value(' '), 'lastname')
    # )

    # print(stars_queryset)
    # star_data = list(stars_queryset.values_list(
    #     'id',
    #     'name'
    # ))
    # print(star_data)
        
    # return JsonResponse(star_data, safe=False)
