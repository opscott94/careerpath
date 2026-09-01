from django.contrib import admin
from django.urls import path, include

from django.http import JsonResponse

admin.site.site_header = "CareerPath Ghana Administration"
admin.site.site_title = "CareerPath Ghana Admin Portal"
admin.site.index_title = "Academic & Admissions Data Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ping/', lambda r: JsonResponse({'status': 'ok'})),
    path('', include('frontend.urls')),
    path('api/', include('api.urls')),
]

