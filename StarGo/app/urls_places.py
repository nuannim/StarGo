from django.urls import path

from . import views

urlpatterns = [
    path("", views.places, name="places"),
    path("<int:places_id>/", views.places_sortby, name="places_sortby"),
    path("addnewplace/", views.places_addnewplace, name="places_addnewplace"),
    path("editplace/<int:places_id>/", views.places_edit, name="places_edit"),
    path("delete/<int:places_id>/", views.places_delete, name="places_delete"),

    # path("sortby/<int:places_id>", views.place_sortby, name="place_sortby"),
]
