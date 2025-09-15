# apps/users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from .models import User
import uuid

# 3단계에서 만든 Supabase 클라이언트 인스턴스를 가져옵니다.
from backend.supabase_client import supabase

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # 디버깅을 위한 출력
        print("Request data:", request.data)
        
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        nickname = serializer.validated_data.get('nickname')
        
        try:
            # 1. Supabase 클라이언트를 사용하여 Supabase Auth에 사용자 생성
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            # Supabase Auth에서 반환된 user 객체
            supabase_user = auth_response.user
            
            if supabase_user:
                # 2. Django 데이터베이스에 Supabase user.id와 함께 사용자 정보 저장
                # UUID를 문자열로 변환하여 저장
                user = User.objects.create(
                    id=str(supabase_user.id),  # UUID를 문자열로 변환
                    email=email,
                    nickname=nickname,
                    password='',  # 빈 문자열 또는 더미 값 설정
                )
                
                return Response(
                    {
                        "message": "User created successfully. Please check your email for verification.",
                        "user_id": user.id
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response({"error": "Supabase user creation failed"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Supabase API 에러 처리
            print("Supabase error:", str(e))
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)