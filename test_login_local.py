"""
로컬 환경에서 로그인 API 테스트
"""
import requests
import json

# 로컬 서버 URL
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/users/login/"

def test_login(email, password):
    """로그인 테스트"""
    print(f"\n{'='*60}")
    print(f"로그인 테스트 시작")
    print(f"Email: {email}")
    print(f"URL: {LOGIN_URL}")
    print(f"{'='*60}\n")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        print("요청 전송 중...")
        response = requests.post(
            LOGIN_URL,
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
        
        if response.status_code == 200:
            print("\n✅ 로그인 성공!")
            return True
        else:
            print("\n❌ 로그인 실패")
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

def test_simple():
    """미리 정의된 테스트"""
    # 여기에 테스트 계정 정보를 입력하세요
    TEST_EMAIL = "testemail@example.com"  # 실제 테스트 계정으로 변경
    TEST_PASSWORD = "testpassword12345"  # 실제 비밀번호로 변경
    
    if TEST_EMAIL == "test@example.com":
        print("\n⚠️  test_simple() 함수의 TEST_EMAIL과 TEST_PASSWORD를 실제 값으로 변경하세요")
        return False
    
    return test_login(TEST_EMAIL, TEST_PASSWORD)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║           로컬 로그인 API 테스트                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("테스트 방법 선택:")
    print("1. 직접 입력")
    print("2. 코드에 저장된 테스트 계정 사용 (test_simple)")
    
    choice = input("\n선택 (1 또는 2): ").strip()
    
    if choice == "2":
        test_simple()
    else:
        # 테스트할 이메일과 비밀번호 입력
        print("\n테스트할 계정 정보를 입력하세요:")
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if email and password:
            test_login(email, password)
        else:
            print("\n❌ 이메일과 비밀번호를 모두 입력해야 합니다.")

