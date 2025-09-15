# backend/supabase_client.py
from django.conf import settings
from supabase import create_client, Client

# settings.py에서 설정 값을 가져와 Supabase 클라이언트 인스턴스를 생성합니다.
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)