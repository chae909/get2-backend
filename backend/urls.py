from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('apps.users.urls')), # 'apps.' 경로 추가
    path('ai/', include('ai_service.urls')),
]