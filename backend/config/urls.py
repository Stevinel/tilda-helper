from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.orders.urls")),
]

admin.site.site_header = "Hush Time Administrator"
admin.site.index_title = "Hush Time Administrator"
admin.site.site_title = "Hush Time Administrator"
admin.site.unregister(Group)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
