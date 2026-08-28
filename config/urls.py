from django.contrib import admin
from django.urls import path, include

from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ping/', lambda r: JsonResponse({'status': 'ok'})),
    path('', include('frontend.urls')),
    path('api/', include('api.urls')),
]

