# backend/supabase_client.py
from django.conf import settings
from supabase import create_client, Client
from typing import Optional

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Supabase 클라이언트를 lazy loading 방식으로 반환
    서버 시작 시 초기화 문제 방지
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    return _supabase_client

# 하위 호환성을 위한 속성
@property
def supabase() -> Client:
    return get_supabase_client()