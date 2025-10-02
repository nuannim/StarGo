from django.http import JsonResponse
from django.shortcuts import render, redirect


from app.forms import *
from .models import *
from django.db.models.functions import Concat
from django.db.models import Value

# Create your views here.
def index(request):
    return render(request, 'index.html')

def sightings(request, celebrities_id):
    celebrities = Celebrities.objects.get(id=celebrities_id)

    if request.method == 'GET':
        form = SightingsForm()
    else:
        form = SightingsForm(request.POST)
        if form.is_valid():
            sighting = form.save(commit=False)
            sighting.celebrities = Celebrities.objects.get(id=celebrities_id)
            # sighting.addby_users = request.user
            sighting.save()

            print(sighting.places)
            print(sighting.arrivaldate)
            print(sighting.celebrities)
            print(sighting.addby_users)

            form = SightingsForm()
            return redirect('sightings', celebrities_id=celebrities_id)
        
    context = {
        'form': form,
        'celebrities_id': celebrities_id,
        'celebrities': celebrities,
    }

    return render(request, 'sightings.html', context)

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
    # groups = Groups.objects.all()

    if request.method == 'GET':
        form = CelebritiesForm()


    else:
        form = CelebritiesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CelebritiesForm()
            return redirect('stars')

    context = {
        'form': form,
        # 'groups': groups,
    }


    return render(request, 'stars_addnewstar.html', context)


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
    # print(star_data)

    # * celebrities
    celebrities = Celebrities.objects.get(id=celebrities_id)
    wheretogo = Sightings.objects.filter(celebrities=celebrities_id).order_by('-arrivaldate')
    # print('wheretogo:', wheretogo)

    # print('celebrities.groups.name:', celebrities.groups.all())
    # for i in celebrities.groups.all():
    #     print(i.name)

    context = {
        'star_data': star_data,
        'celebrities': celebrities,
        'wheretogo': wheretogo,
    }

    return render(request, 'stars_sortby.html', context)

# * ===== Places Views =========================
def places(request):
    places = Places.objects.all()
    print('places:', places)
    place_data = list(places.values(
        'id',
        'name'
    ))

    context = {
        'place_data': place_data,
    }

    return render(request, 'places.html', context)


def places_addnewplace(request):
    if request.method == 'GET':
        form = PlacesForm()
    else:
        form = PlacesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = PlacesForm()
            return redirect('places')

    context = {
        'form': form,
    }

    return render(request, 'places_addnewplace.html', context)


def places_sortby(request, places_id):
    thisplace = Places.objects.get(id=places_id)
    whocamehere = Sightings.objects.filter(places=places_id)
    # print('whocamehere:', whocamehere)

    places = Places.objects.all()
    place_data = list(places.values(
        'id',
        'name'
    ))

    context = {
        'place_data': place_data,
        'thisplace': thisplace,
        'whocamehere': whocamehere
    }

    return render(request, 'places_sortby.html', context)

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
