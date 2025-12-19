# apps/users/views.py
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate, login, logout
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    PasswordChangeSerializer
)
from .models import User
import uuid

# 3단계에서 만든 Supabase 클라이언트 인스턴스를 가져옵니다.
from backend.supabase_client import get_supabase_client


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            # Add detailed error logging for debugging
            print(f"Validation errors: {serializer.errors}")
            print(f"Request data: {request.data}")
            
            # Format errors for frontend
            error_messages = []
            field_errors = {}
            
            for field, errors in serializer.errors.items():
                if field == 'non_field_errors':
                    error_messages.extend([str(error) for error in errors])
                else:
                    field_errors[field] = [str(error) for error in errors]
                    # Also add to general error messages for backwards compatibility
                    error_messages.extend([str(error) for error in errors])
            
            response_data = {
                "error": "입력 데이터가 유효하지 않습니다.",
                "details": field_errors
            }
            
            # Add non_field_errors if there are general error messages
            if error_messages:
                response_data["non_field_errors"] = error_messages
            
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        nickname = serializer.validated_data.get('nickname')
        
        try:
            # 1. Supabase 클라이언트를 사용하여 Supabase Auth에 사용자 생성
            auth_response = get_supabase_client().auth.sign_up({
                "email": email,
                "password": password,
            })
            
            # Supabase Auth에서 반환된 user 객체
            supabase_user = auth_response.user
            
            if supabase_user:
                try:
                    # 2. Django 데이터베이스에 Supabase user.id와 함께 사용자 정보 저장
                    user = User.objects.create_user(
                        id=str(supabase_user.id),
                        email=email,
                        nickname=nickname,
                        password='',  # Supabase에서 관리하므로 빈 값
                        first_name='',  # 기본값 설정
                        last_name='',   # 기본값 설정
                        is_active=True,  # 활성 상태로 설정
                    )
                except Exception as django_error:
                    # Django 사용자 생성 실패 시 Supabase 사용자 삭제 시도
                    try:
                        get_supabase_client().auth.admin.delete_user(str(supabase_user.id))
                    except:
                        pass  # Supabase 삭제 실패는 무시 (수동으로 정리 필요)
                    
                    raise django_error
                
                return Response(
                    {
                        "message": "회원가입이 완료되었습니다.",
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "nickname": user.nickname
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": "회원가입에 실패했습니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            error_message = str(e)
            
            # Supabase 에러와 Django 에러를 구분하여 처리
            if "auth" in error_message.lower() or "supabase" in error_message.lower():
                return Response(
                    {"error": f"Supabase 인증 오류: {error_message}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif "duplicate" in error_message.lower() or "unique" in error_message.lower():
                return Response(
                    {"error": "이미 존재하는 이메일 또는 닉네임입니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": f"회원가입 중 오류가 발생했습니다: {error_message}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )


logger = logging.getLogger(__name__)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Login attempt for email: {request.data.get('email', 'N/A')}")
        
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            logger.warning(f"Login validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        logger.info(f"Starting Supabase auth for: {email}")
        
        try:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
            
            def supabase_login():
                logger.debug("Calling Supabase sign_in_with_password")
                try:
                    result = get_supabase_client().auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    logger.debug(f"Supabase response received for {email}")
                    return result
                except Exception as e:
                    logger.error(f"Supabase login error: {str(e)}")
                    raise
            
            # 타임아웃 20초 설정
            logger.debug("Creating ThreadPoolExecutor for Supabase call")
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(supabase_login)
                try:
                    auth_response = future.result(timeout=20)
                    logger.info(f"Supabase auth completed for {email}")
                except FuturesTimeoutError:
                    logger.error(f"Supabase auth timeout for {email}")
                    return Response(
                        {"error": "로그인 요청 시간이 초과되었습니다. 다시 시도해주세요."}, 
                        status=status.HTTP_408_REQUEST_TIMEOUT
                    )
                except Exception as e:
                    logger.error(f"ThreadPoolExecutor error: {str(e)}")
                    raise
            
            if auth_response and auth_response.user:
                logger.info(f"Supabase auth successful for {email}")
                # Django 유저 객체 가져오기
                try:
                    user = User.objects.get(email=email)
                    logger.debug(f"Django user found: {user.id}")
                except User.DoesNotExist:
                    logger.error(f"Django user not found for email: {email}")
                    return Response(
                        {"error": "사용자를 찾을 수 없습니다."}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # JWT 토큰 생성
                refresh = RefreshToken.for_user(user)
                logger.info(f"JWT tokens generated for user: {user.id}")
                
                return Response({
                    "message": "로그인 성공",
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "nickname": user.nickname
                    },
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    },
                    "supabase_session": {
                        "access_token": auth_response.session.access_token,
                        "refresh_token": auth_response.session.refresh_token
                    }
                }, status=status.HTTP_200_OK)
            
            else:
                logger.warning(f"Supabase auth failed for {email}")
                return Response(
                    {"error": "이메일 또는 비밀번호가 올바르지 않습니다."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"Login error for {email}: {error_message}", exc_info=True)
            
            # 이메일 인증 관련 에러 처리
            if "email not confirmed" in error_message.lower() or "email_confirmed_at" in error_message.lower():
                return Response(
                    {
                        "error": "이메일 인증이 필요합니다. 이메일을 확인해주세요.",
                        "error_type": "email_not_confirmed"
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"error": f"로그인 중 오류가 발생했습니다: {error_message}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Supabase 로그아웃
            get_supabase_client().auth.sign_out()
            
            # JWT 토큰 무효화 (refresh token이 있는 경우)
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response(
                {"message": "로그아웃이 완료되었습니다."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"로그아웃 중 오류가 발생했습니다: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                # Supabase에서 비밀번호 변경
                get_supabase_client().auth.update_user({
                    "password": serializer.validated_data['new_password']
                })
                
                # Django에서도 업데이트 (동기화)
                serializer.save()
                
                return Response(
                    {"message": "비밀번호가 성공적으로 변경되었습니다."}, 
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """JWT 토큰 갱신"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token이 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh = RefreshToken(refresh_token)
        new_token = refresh.access_token
        
        return Response({
            "access": str(new_token)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"토큰 갱신 실패: {str(e)}"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )