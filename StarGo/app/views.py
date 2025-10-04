from django.http import JsonResponse
from django.shortcuts import render, redirect

from django.db.models.functions import Concat
from django.db.models import Value
from django.db import transaction

from django.views import View
from django.contrib.auth.models import User, Group

from django.contrib import messages
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

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
            try:
                with transaction.atomic():
                    sighting = form.save(commit=False)
                    sighting.celebrities = Celebrities.objects.get(id=celebrities_id)
                    myuser = User.objects.get(username=request.user)
                    sighting.addby_auth_user = myuser                    
                    sighting.save()
                    
                    form = SightingsForm()
                    return redirect('sightings', celebrities_id=celebrities_id)
            except Exception as e:
                print(e)
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

    if request.method == 'GET':
        form = CelebritiesForm()

    else:
        form = CelebritiesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    waitforcommit = form.save(commit=False)
                    myuser = User.objects.get(username=request.user)
                    waitforcommit.addby_auth_user = myuser
                    waitforcommit.save()
                    
                    form = CelebritiesForm()
                    return redirect('stars')
            except Exception as e:
                print(e)
    context = {
        'form': form,
    }


    return render(request, 'stars_addnewstar.html', context)


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
@login_required
def places(request):
    places = Places.objects.all()
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
            try:
                with transaction.atomic():
                    waitforcommit = form.save(commit=False)
                    myuser = User.objects.get(username=request.user)
                    waitforcommit.addby_auth_user = myuser
                    waitforcommit.save()

                    form = PlacesForm()
                    return redirect('places')
                
            except Exception as e:
                print(e)
    context = {
        'form': form,
    }

    return render(request, 'places_addnewplace.html', context)


@login_required
def places_sortby(request, places_id):
    thisplace = Places.objects.get(id=places_id)
    whocamehere = Sightings.objects.filter(places=places_id)

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
    users = Users.objects.get(auth_user_id=request.user.id)
    auth_user = User.objects.get(pk=request.user.id)
    # print('requset auth_user', auth_user)

    context = {
        'users': users,
        'auth_user': auth_user,

    }

    return render(request, 'profile.html', context)

@login_required
def profile_edit(request):
    users = Users.objects.get(auth_user_id=request.user.id)
    # auth_user = User.objects.get(pk=request.user.id)
    auth_user = request.user

    if request.method == 'GET':
        profileform = ProfileEditForm(instance=auth_user)
        profileimageform = ProfileImageEditForm(instance=users)

    else:
        profileform = ProfileEditForm(request.POST, instance=auth_user)
        profileimageform = ProfileImageEditForm(request.POST, request.FILES, instance=users)
        print('requset files', request.FILES)

        if request.POST.get('action') == 'remove_photo' and users.imageurl:
            users.imageurl.delete(save=False)
            users.save()
            return redirect('profile_edit')

        if profileform.is_valid() or profileimageform.is_valid():
            try:
                with transaction.atomic():
                    profileform.save()
                    profileimageform.save()
                    profileform = ProfileEditForm(instance=auth_user)
                    profileimageform = ProfileImageEditForm(instance=users)

                    return redirect('profile_edit')

            except Exception as e:
                print(e)

    context = {
        'users': users,
        'auth_user': auth_user,
        'profileform': profileform,
        'profileimageform': profileimageform
    }

    return render(request, 'profile_edit.html', context)

@login_required
def profile_changepassword(request):
    if request.method == 'GET':
        form = CustomPasswordChangeForm(user=request.user)
    else:
        form = CustomPasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form1 = form.save()
                    update_session_auth_hash(request, form1)
                    messages.success(request, 'Your password was successfully updated!')

                    return redirect('profile_changepassword')

            except Exception as e:
                print(e)

    context = {
        'form': form
    }

    return render(request, 'profile_changepassword.html', context)


@login_required
def profile_deleteaccount(request):
    if request.method == 'POST':
        myuser = request.user
        myuser.is_active = False
        myuser.save()
        logout(request)

        messages.success(request, 'Your account has been deleted')

        return redirect('loginpage')

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
        if form.is_valid():

            try:
                with transaction.atomic():
                    user = form.save()
                    usergroup = Group.objects.get(name='user')
                    user.groups.add(usergroup)
                    
                    Users.objects.create(
                        auth_user=user,
                    )

                    login(request, user)
                    # messages.success(request, "Registration successful." )


                    return redirect('places')
            except Exception as e:
                print(e)
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")

    context = {
        'form': form
    }

    return render (request, 'registerpage.html', context)

@login_required
def bands(request):
    if request.method == 'GET':
        form = BandsForm()
    else:
        form = BandsForm(request.POST, request.FILES)
        with transaction.atomic():
            if form.is_valid():
                groupnotsave = form.save(commit=False)

                print('request.user:', request.user)

                myuser = User.objects.get(username=request.user)
                print(myuser)
                groupnotsave.addby_auth_user = myuser

                groupnotsave.save()

                form = BandsForm()
                return redirect('bands')

    context = {
        'form': form,
    }

    return render(request, 'bands.html', context)


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
