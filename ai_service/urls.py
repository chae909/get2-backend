# ai_service/urls.py (새 파일)

from django.urls import path
from . import views

urlpatterns = [
    # 'http://.../ai/ask/' 주소로 요청이 오면 views.py의 ask_ai 함수를 실행
    path('ask/', views.ask_ai, name='ask_ai'),
]