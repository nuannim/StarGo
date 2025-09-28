from django.urls import path

from . import views

urlpatterns = [
    path("", views.places, name="places"),
    path("addnewplace/", views.places_addnewplace, name="places_addnewplace"),
    path("sortby/", views.places_sortby, name="places_sortby"),

    # path("sortby/<int:places_id>", views.place_sortby, name="place_sortby"),
]
