from django.http import JsonResponse
from django.shortcuts import render, redirect

from django.db.models.functions import Concat
from django.db.models import Value

from django.views import View
from django.contrib.auth.models import User, Group


from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction


from app.forms import *
from .models import *


# Create your views here.
def index(request):
    return render(request, 'index.html')

@login_required
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

            # print(sighting.places)
            # print(sighting.arrivaldate)
            # print(sighting.celebrities)
            # print(sighting.addby_users)

            form = SightingsForm()
            return redirect('sightings', celebrities_id=celebrities_id)
        
    context = {
        'form': form,
        'celebrities_id': celebrities_id,
        'celebrities': celebrities,
    }

    return render(request, 'sightings.html', context)

# * ===== Stars Views ===========================

@login_required
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

@login_required
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


@login_required
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
@login_required
def places(request):
    places = Places.objects.all()
    # print('places:', places)
    place_data = list(places.values(
        'id',
        'name'
    ))

    context = {
        'place_data': place_data,
    }

    return render(request, 'places.html', context)


@login_required
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


@login_required
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
@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def profile_edit(request):
    return render(request, 'profile_edit.html')

@login_required
def profile_changepassword(request):
    return render(request, 'profile_changepassword.html')

@login_required
def profile_deleteaccount(request):
    return render(request, 'profile_deleteaccount.html')


# * ===== Login/Logout Authentication ==========================
def loginpage(request):
    if request.method == 'GET':
        form = AuthenticationForm()
        
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('places')
        else:
            messages.error(request, 'Invalid username or password')

    context = {
            'form': form
        }

    return render(request, 'login.html', context)


@login_required
def logoutpage(request):
    logout(request)
    return redirect('loginpage')

# * ===== Create Account ========================
def registerpage(request):
    if request.method == 'GET':
        form = CustomUserCreationForm()
    else:
        form = CustomUserCreationForm(request.POST)
        with transaction.atomic():
        
            if form.is_valid():
                user = form.save()
                usergroup = Group.objects.get(name='user')
                user.groups.add(usergroup)
                
                Users.objects.create(
                    auth_user=user,
                )

                login(request, user)
                # messages.success(request, "Registration successful." )


                return redirect('places')
            messages.error(request, "Unsuccessful registration. Invalid information.")

    context = {
        'form': form
    }

    return render (request, 'registerpage.html', context)


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
