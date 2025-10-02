#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 API 테스트 스크립트
파티 플래닝 AI 에이전트 API가 정상 작동하는지 확인합니다.
"""

import requests
import json
from datetime import datetime, timedelta

def test_health_endpoint():
    """헬스 체크 엔드포인트 테스트"""
    print("🔍 헬스 체크 테스트...")
    try:
        response = requests.get('http://localhost:8000/api/v1/ai/health/', timeout=10)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print(f"   응답: {response.json()}")
            return True
        else:
            print(f"   오류: {response.text}")
            return False
    except Exception as e:
        print(f"   연결 오류: {e}")
        return False

def test_simple_ai_question():
    """간단한 AI 질문 테스트"""
    print("\n🤖 AI 질답 테스트...")
    data = {
        "question": "안녕하세요! 파티 준비에 대해 간단한 조언 부탁드립니다.",
        "context": {"domain": "party_planning"}
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/ai/ask/',
            json=data,
            timeout=30
        )
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   AI 응답: {result.get('answer', 'N/A')[:100]}...")
            return True
        else:
            print(f"   오류: {response.text}")
            return False
    except Exception as e:
        print(f"   연결 오류: {e}")
        return False

def test_party_planning():
    """파티 플래닝 테스트"""
    print("\n🎉 파티 플래닝 테스트...")
    
    # 간단한 테스트 데이터
    data = {
        "party_type": "생일파티",
        "guest_count": 10,
        "date": (datetime.now() + timedelta(days=7)).isoformat(),
        "budget": 200000,
        "location": "서울",
        "special_requirements": "간단한 홈파티"
    }
    
    print("   요청 데이터:")
    print(f"     파티 종류: {data['party_type']}")
    print(f"     참석자: {data['guest_count']}명")
    print(f"     예산: {data['budget']:,}원")
    print(f"     장소: {data['location']}")
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/ai/party/plan/',
            json=data,
            timeout=60
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 성공!")
            print(f"   계획 ID: {result.get('plan_id', 'N/A')}")
            
            if result.get('estimated_cost'):
                print(f"   예상 비용: {result['estimated_cost']:,.0f}원")
            
            if result.get('tasks'):
                print(f"   할일 개수: {len(result['tasks'])}개")
                
            if result.get('timeline'):
                print(f"   타임라인 단계: {len(result['timeline'])}개")
                
            if result.get('overall_plan'):
                plan_preview = result['overall_plan'][:200] + "..." if len(result['overall_plan']) > 200 else result['overall_plan']
                print(f"   계획 미리보기: {plan_preview}")
                
            return True
        else:
            print(f"   ❌ 오류: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 연결 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 파티 플래닝 AI 에이전트 API 테스트")
    print("=" * 50)
    
    # 각 테스트 실행
    tests = [
        ("헬스 체크", test_health_endpoint),
        ("AI 질답", test_simple_ai_question),
        ("파티 플래닝", test_party_planning)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("-" * 30)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n총 {len(tests)}개 테스트 중 {success_count}개 성공")
    
    if success_count == len(tests):
        print("🎉 모든 테스트 성공! AI 에이전트가 정상 작동합니다.")
    elif success_count > 0:
        print("⚠️ 일부 테스트 성공. 시스템이 부분적으로 작동합니다.")
    else:
        print("❌ 모든 테스트 실패. 시스템을 확인해주세요.")

if __name__ == "__main__":
    main()