from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API 엔드포인트
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/plans/', include('apps.plans.urls')),
    path('api/v1/ai/', include('ai_service.urls')),
    
    # JWT 토큰 엔드포인트
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]