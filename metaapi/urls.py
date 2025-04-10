from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView  # Add this import
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.urls import re_path

urlpatterns = [
    path('dashboard/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='metaapi/base.html'), name='base'),  # Add this line
]

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)