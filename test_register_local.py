"""
로컬 환경에서 회원가입 API 테스트
"""
import requests
import json

# 로컬 서버 URL
BASE_URL = "http://127.0.0.1:8000"
REGISTER_URL = f"{BASE_URL}/api/v1/users/register/"

def test_register(email, nickname, password):
    """회원가입 테스트"""
    print(f"\n{'='*60}")
    print(f"회원가입 테스ト 시작")
    print(f"Email: {email}")
    print(f"Nickname: {nickname}")
    print(f"URL: {REGISTER_URL}")
    print(f"{'='*60}\n")
    
    payload = {
        "email": email,
        "nickname": nickname,
        "password": password,
        "password_confirm": password
    }
    
    try:
        print("요청 전송 중...")
        response = requests.post(
            REGISTER_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n상태 코드: {response.status_code}")
        print(f"응답 시간: {response.elapsed.total_seconds():.2f}초")
        
        print(f"\n응답 본문:")
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        
        if response.status_code == 201:
            print("\n✅ 회원가입 성공!")
            print("⚠️  이메일 인증 링크를 확인하세요!")
            return True
        else:
            print("\n❌ 회원가입 실패")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ 타임아웃 발생 (30초 초과)")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ 연결 실패 - 서버가 실행 중인지 확인하세요")
        print("   python manage.py runserver 명령으로 서버를 시작하세요")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║           로컬 회원가입 API 테스트                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("새 계정 정보를 입력하세요:")
    email = input("Email: ").strip()
    nickname = input("Nickname: ").strip()
    password = input("Password: ").strip()
    
    if email and nickname and password:
        test_register(email, nickname, password)
    else:
        print("\n❌ 모든 정보를 입력해야 합니다.")
