import requests
import json
from datetime import datetime, timedelta

# 테스트 데이터
test_data = {
    "party_type": "생일파티",
    "guest_count": 15,
    "date": (datetime.now() + timedelta(days=14)).isoformat(),
    "budget": 300000,
    "location": "강남구",
    "special_requirements": "케이크와 장식 중심의 파티",
    "dietary_restrictions": ["vegetarian"]
}

print("🎉 파티 플래닝 API 테스트")
print("=" * 40)
print("요청 데이터:")
print(json.dumps(test_data, indent=2, ensure_ascii=False))
print()

try:
    # API 호출
    response = requests.post(
        'http://localhost:8000/api/v1/ai/party/plan/',
        json=test_data,
        timeout=60
    )
    
    print(f"응답 상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 성공!")
        print()
        print(f"계획 ID: {result.get('plan_id', 'N/A')}")
        print(f"예상 비용: {result.get('estimated_cost', 'N/A'):,}원" if result.get('estimated_cost') else "예상 비용: 계산 중")
        print()
        print("전체 계획:")
        print(result.get('overall_plan', '계획 생성 중...'))
        
    else:
        print("❌ 오류 발생")
        print(f"응답: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 연결 오류: {e}")