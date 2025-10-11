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

import requests
import os

STORAGE_API_URL = os.environ.get("STORAGE_API_URL", "http://127.0.0.1:8001")
# Normalize STORAGE API base: ensure it points to the storage app root that contains the API
# storage_microservice mounts its app under /api/, so prefer that unless caller already included it.
if STORAGE_API_URL.endswith('/'):
    STORAGE_API_URL = STORAGE_API_URL[:-1]
if '/api' not in STORAGE_API_URL:
    STORAGE_API_BASE = STORAGE_API_URL + '/api'
else:
    STORAGE_API_BASE = STORAGE_API_URL

# Create your views here.
def index(request):
    return render(request, 'index.html')


# small helper used to adapt model instances so templates that call <obj>.imageurl.url
# will get an absolute URL when the stored value is an absolute URL from the storage microservice.
class URLHolder:
    def __init__(self, url):
        self.url = url


def ensure_image_url(obj):
    """If obj.imageurl contains an absolute URL (or a name that starts with http), replace
    obj.imageurl with a tiny object that exposes a .url attribute pointing to that absolute URL.
    This keeps templates that call `{{ instance.imageurl.url }}` working without changing models.
    """
    if not obj:
        return
    try:
        val = getattr(obj, 'imageurl')
    except Exception:
        return
    if not val:
        return

    # If it's already a URLHolder, leave it
    if isinstance(val, URLHolder):
        return

    # If it's a plain string (unlikely for FieldFile access, but handle it)
    if isinstance(val, str):
        if val.startswith('http://') or val.startswith('https://'):
            obj.imageurl = URLHolder(val)
        return

    # FieldFile-like object: check .name for an absolute URL
    try:
        name = getattr(val, 'name', None)
        if isinstance(name, str) and (name.startswith('http://') or name.startswith('https://')):
            obj.imageurl = URLHolder(name)
    except Exception:
        return

@login_required
def sightings_stars(request, celebrities_id):
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
                    return redirect('sightings_stars', celebrities_id=celebrities_id)
            except Exception as e:
                print(e)
    context = {
        'form': form,
        'celebrities_id': celebrities_id,
        'celebrities': celebrities,
    }

    return render(request, 'sightings_stars.html', context)


@login_required
def sightings(request):
    # if request.method == 'GET':
    #     form = SightingsForm2()

    getsource = None

    if request.method == 'GET':
        # สร้าง Dictionary ว่างๆ เพื่อเก็บค่าเริ่มต้น
        initial_data = {}

        # ตรวจสอบว่ามี star_id ส่งมาใน URL หรือไม่
        celebritiesIdFromURL = request.GET.get('celebrities_id')
        if celebritiesIdFromURL:
            # ถ้ามี, กำหนดค่าเริ่มต้นให้กับฟิลด์ 'celebrities'
            initial_data['celebrities'] = celebritiesIdFromURL
            getsource = 'celebrities'

        # ตรวจสอบว่ามี place_id ส่งมาใน URL หรือไม่
        placeIdFromURL = request.GET.get('place_id')
        if placeIdFromURL:
            # ถ้ามี, กำหนดค่าเริ่มต้นให้กับฟิลด์ 'places'
            initial_data['places'] = placeIdFromURL
            getsource = 'places'

        # สร้างฟอร์มโดยส่ง initial_data เข้าไป
        # Django จะนำค่า id ไปเลือก option ใน dropdown ให้เองอัตโนมัติ
        form = SightingsForm2(initial=initial_data)
    else:
        form = SightingsForm2(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    sight = form.save(commit=False)
                    # myuser = User.objects.get(username=request.user)
                    # sight.addby_auth_user = myuser
                    sight.addby_auth_user = request.user
                    sight.save()

                    # form = SightingsForm2()

                    postsource = request.POST.get('source')

                    if postsource == 'celebrities':
                        c_id = form.cleaned_data['celebrities'].id
                        return redirect('stars_sortby', celebrities_id=c_id)
                    
                    elif postsource == 'places':
                        p_id = form.cleaned_data['places'].id
                        return redirect('places_sortby', places_id=p_id)
                    
                    return redirect('places')

            except Exception as e:
                print('error from def sightings POST method:', e)

    context = {
        'form': form,
        'getsource': getsource
    }
    return render(request, 'sightings.html', context)


@login_required
def sightings_edit(request, sightings_id):
    sightings = Sightings.objects.get(pk=sightings_id)
    print('sightings:', sightings)

    # * เอาไว้ดัก ถ้าไม่ได้สร้าง sightings นี้ ให้ redirect ไปที่ profile
    if sightings.addby_auth_user != request.user:
        messages.error(request, "You do not have permission to edit that sighting.")
        return redirect('profile') 

    if request.method == 'GET':
        form = SightingsForm2(instance=sightings)
    else:
        form = SightingsForm2(request.POST, instance=sightings)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    form = SightingsForm2(instance=sightings)

                    return redirect('sightings_edit', sightings_id=sightings_id)
            except Exception as e:
                print('error from def sightings_edit POST method:', e)

    context = {
        'form': form,
        'sightings_id': sightings_id, 
    }

    return render(request, 'sightings.html', context)



# @login_required
# def sightings_places(request, places_id):
#     places = Places.objects.get(id=places_id)

#     if request.method == 'GET':
#         form = SightingsForm()
#     else:
#         form = SightingsForm(request.POST)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     sighting = form.save(commit=False)
#                     sighting.celebrities
    

# * ===== Stars Views ===========================

@login_required
def stars(request):
    stars_queryset = Celebrities.objects.annotate(
        name=Concat('firstname', Value(' '), 'lastname', Value(' ('), 'nickname', Value(')'))
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
                    celebrity = form.save(commit=False)
                    myuser = User.objects.get(username=request.user)
                    celebrity.addby_auth_user = myuser

                    # Handle image upload to storage-microservice
                    if 'imageurl' in request.FILES:
                        image_file = request.FILES['imageurl']
                        files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
                        response = requests.post(f"{STORAGE_API_BASE}/images/upload/", files=files)
                        if response.status_code == 201:
                            # Save the image URL from the microservice
                            celebrity.imageurl = response.json().get('url')
                        else:
                            # Handle upload error
                            messages.error(request, f"Failed to upload image: {response.text}")
                            raise Exception("Image upload failed")
                    
                    celebrity.save()
                    
                    form = CelebritiesForm()
                    return redirect('stars')
            except Exception as e:
                print(e)
                messages.error(request, f"An error occurred: {e}")
    context = {
        'form': form,
    }


    return render(request, 'stars_addnewstar.html', context)


@login_required
def stars_sortby(request, celebrities_id):
    # * ก้อปมาจาก def stars()
    stars_queryset = Celebrities.objects.annotate(
        name=Concat('firstname', Value(' '), 'lastname', Value(' ('), 'nickname', Value(')'))
    )
    star_data = list(stars_queryset.values(
        'id',
        'name',
    ))

    # * celebrities
    celebrities = Celebrities.objects.get(id=celebrities_id)
    ensure_image_url(celebrities)
    wheretogo = Sightings.objects.filter(celebrities=celebrities_id).order_by('places', '-arrivaldate').distinct('places')


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

    # profileowner = get_object_or_404(User, username=username)

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
                    place = form.save(commit=False)
                    myuser = User.objects.get(username=request.user)
                    place.addby_auth_user = myuser

                    # Handle image upload to storage-microservice
                    if 'imageurl' in request.FILES:
                        image_file = request.FILES['imageurl']
                        files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
                        response = requests.post(f"{STORAGE_API_BASE}/images/upload/", files=files)
                        if response.status_code == 201:
                            # Save the image URL from the microservice
                            place.imageurl = response.json().get('url')
                        else:
                            # Handle upload error
                            messages.error(request, f"Failed to upload image: {response.text}")
                            raise Exception("Image upload failed")

                    place.save()

                    form = PlacesForm()
                    return redirect('places')
                
            except Exception as e:
                print(e)
                messages.error(request, f"An error occurred: {e}")
    context = {
        'form': form,
    }

    return render(request, 'places_addnewplace.html', context)


@login_required
def places_sortby(request, places_id):
    thisplace = Places.objects.get(id=places_id)
    ensure_image_url(thisplace)
    whocamehere = Sightings.objects.filter(places=places_id).order_by('celebrities').distinct('celebrities')

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
    auth_user = request.user
    users = Users.objects.get(auth_user=auth_user)
    # users = Users.objects.get(auth_user = request.user)
    # auth_user = User.objects.get(pk=request.user.id)

    sightings = Sightings.objects.filter(addby_auth_user=auth_user).distinct()
    places = Places.objects.filter(addby_auth_user=auth_user)
    celebrities = Celebrities.objects.filter(addby_auth_user=auth_user)
    # sightings = Sightings.objects.filter(addby_auth_user_id=request.user.id).distinct()
    # places = Places.objects.filter(addby_auth_user_id=request.user.id)
    # celebrities = Celebrities.objects.filter(addby_auth_user_id=request.user.id)

    print('userid:', request.user.id)
    print('sightings:', sightings)
    print('places:', places)
    print('celebrities:', celebrities)

    context = {
        'users': users,
        'auth_user': auth_user,
        'sightings': sightings,
        'places': places,
        'celebrities': celebrities,
    }

    # ensure any imageurl fields that contain absolute URLs are exposed as .url for templates
    ensure_image_url(users)
    for p in places:
        ensure_image_url(p)
    for c in celebrities:
        ensure_image_url(c)

    return render(request, 'profile.html', context)


# @login_required
def profile_share(request, username):
    user = User.objects.get(username=username)
    users = Users.objects.get(auth_user_id=user.id)

    sightings = Sightings.objects.filter(addby_auth_user=user).distinct()
    places = Places.objects.filter(addby_auth_user=user)
    celebrities = Celebrities.objects.filter(addby_auth_user=user)

    print('user:', user)
    print('users:', users)

    context = {
        'users': users,
        'auth_user': user,
        'sightings': sightings,
        'places': places,
        'celebrities': celebrities,
    }

    # ensure image urls
    ensure_image_url(users)
    for p in places:
        ensure_image_url(p)
    for c in celebrities:
        ensure_image_url(c)

    return render(request, 'profile_share.html', context)



@login_required
def profile_edit(request):
    users = Users.objects.get(auth_user_id=request.user.id)
    auth_user = request.user

    if request.method == 'GET':
        profileform = ProfileEditForm(instance=auth_user)
        profileimageform = ProfileImageEditForm(instance=users)
        # expose absolute image URL for template if needed
        ensure_image_url(users)

    else:
        profileform = ProfileEditForm(request.POST, instance=auth_user)
        profileimageform = ProfileImageEditForm(request.POST, request.FILES, instance=users)

        if request.POST.get('action') == 'remove_photo' and users.imageurl:
            # Extract filename from URL and call delete API
            try:
                filename = users.imageurl.split('/')[-1]
                response = requests.delete(f"{STORAGE_API_BASE}/images/{filename}/delete/")
                if response.status_code not in [200, 204, 404]: # Allow 404 if file not found
                    messages.error(request, f"Failed to delete image: {response.text}")
                    raise Exception("Image deletion failed")
            except Exception as e:
                print(e)
                messages.error(request, f"An error occurred while deleting the image: {e}")
            
            users.imageurl = None # Or set to a default image URL from microservice
            users.save()
            return redirect('profile_edit')

        if profileform.is_valid() or profileimageform.is_valid():
            try:
                with transaction.atomic():
                    profileform.save()
                    
                    # Handle image upload to storage-microservice
                    if 'imageurl' in request.FILES:
                        image_file = request.FILES['imageurl']
                        files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
                        response = requests.post(f"{STORAGE_API_BASE}/images/upload/", files=files)
                        if response.status_code == 201:
                            # Save the image URL from the microservice
                            users.imageurl = response.json().get('url')
                        else:
                            # Handle upload error
                            messages.error(request, f"Failed to upload image: {response.text}")
                            raise Exception("Image upload failed")
                    
                    users.save() # Save the user model with the new image URL

                    return redirect('profile_edit')

            except Exception as e:
                print(e)
                messages.error(request, f"An error occurred: {e}")

    context = {
        'users': users,
        'auth_user': auth_user,
        'profileform': profileform,
        'profileimageform': profileimageform
    }
    return render(request, 'profile_edit.html', context)

    # ensure image url on render (covers POST flows that fall through)
    ensure_image_url(users)
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
