# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    email = serializers.EmailField(required=True)  # 명시적으로 EmailField 추가

    class Meta:
        model = User
        fields = ('email', 'password', 'nickname')

    def validate_email(self, value):
        """이메일 유효성 검사"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_nickname(self, value):
        """닉네임 유효성 검사"""
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def create(self, validated_data):
        # username 없이 email을 사용하여 유저를 생성합니다.
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname']
        )
        return user