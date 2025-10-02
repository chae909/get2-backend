# test_ai_agent.py
"""
파티 플래닝 AI 에이전트 테스트 스크립트
"""

import asyncio
import os
import django
from datetime import datetime, timedelta

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_service.party_planning_agent import PartyPlanningAgent
from ai_service.mcp_integration import mcp_client

async def test_party_planning():
    """파티 플래닝 AI 에이전트 테스트"""
    print("🎉 파티 플래닝 AI 에이전트 테스트 시작")
    print("=" * 50)
    
    # 테스트 데이터
    test_request = {
        'party_type': '생일파티',
        'budget': 300000,
        'guest_count': 15,
        'date': datetime.now() + timedelta(days=14),
        'location': '강남구',
        'special_requirements': '케이크와 장식 중심의 파티',
        'dietary_restrictions': ['vegetarian']
    }
    
    print("📋 테스트 요청 데이터:")
    for key, value in test_request.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        # AI 에이전트 인스턴스 생성
        agent = PartyPlanningAgent()
        print("✅ AI 에이전트 초기화 완료")
        
        # 파티 계획 생성
        print("🤖 AI 에이전트가 파티 계획을 생성 중...")
        result = await agent.create_party_plan(test_request)
        
        print("🎯 파티 계획 생성 완료!")
        print("=" * 50)
        
        # 결과 출력
        print(f"📝 계획 ID: {result['plan_id']}")
        print(f"💰 예상 비용: {result['estimated_cost']:,}원" if result['estimated_cost'] else "💰 예상 비용: 계산 중")
        print()
        
        print("📋 전체 계획:")
        print(result['overall_plan'])
        print()
        
        print("✅ 할일 목록:")
        for i, task in enumerate(result['tasks'], 1):
            print(f"   {i}. {task['task']} ({task['priority']} 우선순위)")
            print(f"      설명: {task['description']}")
            print(f"      마감: {task['deadline']}")
            print()
        
        print("📅 타임라인:")
        for timeline_item in result['timeline']:
            print(f"   {timeline_item['date']} ({timeline_item['day_description']})")
            for task in timeline_item['tasks']:
                print(f"      - {task}")
            print()
        
        print("💡 추천사항:")
        for rec in result['recommendations']:
            print(f"   [{rec['category']}] {rec['suggestion']}")
        
        print("=" * 50)
        print("✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

async def test_mcp_tools():
    """MCP 도구 테스트"""
    print("\n🔧 MCP 도구 테스트 시작")
    print("=" * 30)
    
    try:
        # 장소 검색 테스트
        print("🏢 장소 검색 테스트...")
        venue_result = await mcp_client.call_tool(
            "party_planning",
            "search_venues",
            {"location": "강남구", "capacity": 15}
        )
        print(f"   결과: {len(venue_result.get('venues', []))}개 장소 찾음")
        
        # 케이터링 옵션 테스트
        print("🍽️ 케이터링 옵션 테스트...")
        catering_result = await mcp_client.call_tool(
            "party_planning",
            "get_catering_options",
            {"guest_count": 15, "budget_per_person": 20000}
        )
        print(f"   결과: {len(catering_result.get('catering_options', []))}개 옵션 찾음")
        
        # 예산 계산 테스트
        print("💰 예산 계산 테스트...")
        budget_result = await mcp_client.call_tool(
            "party_planning",
            "calculate_budget",
            {"party_type": "생일파티", "guest_count": 15}
        )
        print(f"   결과: 총 예산 {budget_result['breakdown']['total']:,.0f}원")
        
        print("✅ MCP 도구 테스트 완료!")
        
    except Exception as e:
        print(f"❌ MCP 도구 테스트 오류: {e}")

if __name__ == "__main__":
    print("🚀 파티 플래닝 AI 시스템 종합 테스트")
    print("=" * 60)
    
    # 비동기 테스트 실행
    asyncio.run(test_mcp_tools())
    asyncio.run(test_party_planning())