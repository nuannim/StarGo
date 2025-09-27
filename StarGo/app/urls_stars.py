from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from . import views

urlpatterns = [
    path("", views.stars, name="stars"),
    path("addnewstar/", views.stars_addnewstar, name="stars_addnewstar"),
    # path("sortby/<int:celebrities_id>", views.stars_sortby, name="stars_sortby"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)