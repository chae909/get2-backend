# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'nickname')

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

    def validate(self, attrs):
        """전체 데이터 검증"""
        errors = {}
        
        # 비밀번호 확인 검증
        if attrs.get('password') != attrs.get('password_confirm'):
            errors['password_confirm'] = ["비밀번호가 일치하지 않습니다."]
        
        # 이메일 중복 검사 (필드별 검증에서 놓친 경우 대비)
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            errors['email'] = ["이미 사용 중인 이메일입니다."]
        
        # 닉네임 중복 검사 (필드별 검증에서 놓친 경우 대비)
        nickname = attrs.get('nickname')
        if nickname and User.objects.filter(nickname=nickname).exists():
            errors['nickname'] = ["이미 사용 중인 닉네임입니다."]
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")
        
        # 기본적인 이메일 형식 검증은 EmailField에서 처리됨
        # Supabase Auth에서 실제 인증을 처리하므로 여기서는 기본 validation만 수행
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'nickname', 'date_joined', 'is_active')
        read_only_fields = ('id', 'email', 'date_joined', 'is_active')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("기존 비밀번호가 올바르지 않습니다.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user