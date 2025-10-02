# ai_service/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API 라우터 설정
router = DefaultRouter()

urlpatterns = [
    # 기본 AI 질답 엔드포인트
    path('ask/', views.ask_ai, name='ask_ai'),
    
    # 파티 플래닝 전용 엔드포인트
    path('party/plan/', views.plan_party, name='plan_party'),
    
    # 서비스 상태 확인
    path('health/', views.health_check, name='health_check'),
    
    # 라우터 URL 포함
    path('', include(router.urls)),
]