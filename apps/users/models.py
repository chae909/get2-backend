# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    # Supabase Auth의 user.id는 UUID 타입이므로, 이를 저장할 필드를 추가합니다.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 이메일 필드를 unique=True 속성으로 명시적으로 정의합니다.
    email = models.EmailField(unique=True) # <-- 이 줄을 추가하세요.

    nickname = models.CharField(max_length=50, unique=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']