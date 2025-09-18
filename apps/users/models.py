from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        """
        username 없이 email과 nickname으로 사용자 생성
        """
        if not email:
            raise ValueError('이메일은 필수입니다.')
        if not nickname:
            raise ValueError('닉네임은 필수입니다.')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        """
        슈퍼유저 생성
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('슈퍼유저는 is_staff=True여야 합니다.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('슈퍼유저는 is_superuser=True여야 합니다.')

        return self.create_user(email, nickname, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']
    
    # 커스텀 UserManager 사용
    objects = UserManager()