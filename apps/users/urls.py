from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    refresh_token_view
)

urlpatterns = [
    # 회원가입
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    
    # 로그인/로그아웃
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    
    # 프로필 관리
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # 비밀번호 변경
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # JWT 토큰 갱신
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('refresh/', refresh_token_view, name='refresh-token'),
]