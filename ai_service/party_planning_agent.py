# ai_service/party_planning_agent.py

import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from decimal import Decimal

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# RAG 시스템과 MCP 클라이언트 가져오기
# from .rag_system import PartyPlanningRAG
from .mcp_integration import mcp_client

import logging

logger = logging.getLogger(__name__)

class PartyPlanState(TypedDict):
    """파티 플래닝 상태 정의"""
    # 입력 정보
    party_type: str
    budget: Optional[Decimal]
    guest_count: int
    date: datetime
    location: Optional[str]
    special_requirements: Optional[str]
    dietary_restrictions: List[str]
    
    # 대화 메시지
    messages: Annotated[List, add_messages]
    
    # 생성된 계획
    plan_id: str
    overall_plan: str
    tasks: List[Dict]
    estimated_cost: Optional[Decimal]
    timeline: List[Dict]
    recommendations: List[Dict]
    
    # 중간 상태
    current_step: str
    rag_context: str
    iteration_count: int

class PartyPlanningAgent:
    """파티 플래닝을 위한 LangGraph 에이전트"""
    
    def __init__(self):
        # OpenAI 모델 초기화
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2000
        )
        
        # RAG 시스템 초기화 (임시로 주석 처리)
        # self.rag = PartyPlanningRAG()
        
        # MCP 클라이언트 초기화
        self.mcp_client = mcp_client
        
        # 그래프 빌더 초기화
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """LangGraph 워크플로우 구성"""
        graph_builder = StateGraph(PartyPlanState)
        
        # 노드 정의
        graph_builder.add_node("analyze_requirements", self._analyze_requirements)
        graph_builder.add_node("search_knowledge", self._search_knowledge)
        graph_builder.add_node("generate_plan", self._generate_plan)
        graph_builder.add_node("create_tasks", self._create_tasks)
        graph_builder.add_node("estimate_costs", self._estimate_costs)
        graph_builder.add_node("create_timeline", self._create_timeline)
        graph_builder.add_node("finalize_plan", self._finalize_plan)
        
        # 워크플로우 정의
        graph_builder.set_entry_point("analyze_requirements")
        
        # 조건부 엣지 추가
        graph_builder.add_edge("analyze_requirements", "search_knowledge")
        graph_builder.add_edge("search_knowledge", "generate_plan")
        graph_builder.add_edge("generate_plan", "create_tasks")
        graph_builder.add_edge("create_tasks", "estimate_costs")
        graph_builder.add_edge("estimate_costs", "create_timeline")
        graph_builder.add_edge("create_timeline", "finalize_plan")
        graph_builder.add_edge("finalize_plan", END)
        
        return graph_builder.compile()
    
    async def _analyze_requirements(self, state: PartyPlanState) -> PartyPlanState:
        """요구사항 분석 노드"""
        logger.info("요구사항 분석 시작")
        
        # 시스템 메시지 구성
        system_message = """당신은 전문 파티 플래너입니다. 
        고객의 요구사항을 분석하여 파티 기획의 핵심 포인트를 파악해주세요.
        
        분석해야 할 항목:
        1. 파티의 주요 목적과 분위기
        2. 예산 범위와 우선순위
        3. 참석자 특성 (연령대, 관계 등)
        4. 특별한 요구사항이나 제약사항
        5. 식단 제한사항 고려사항
        
        간결하고 명확하게 분석 결과를 정리해주세요."""
        
        # 사용자 요구사항 정리
        user_input = f"""
        파티 종류: {state['party_type']}
        예산: {state.get('budget', '미정')}원
        참석자 수: {state['guest_count']}명
        날짜: {state['date'].strftime('%Y년 %m월 %d일')}
        장소: {state.get('location', '미정')}
        특별 요구사항: {state.get('special_requirements', '없음')}
        식단 제한: {', '.join(state.get('dietary_restrictions', [])) or '없음'}
        """
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_input)
        ]
        
        # LLM 호출
        response = await self.llm.ainvoke(messages)
        
        # 상태 업데이트
        state['messages'] = [SystemMessage(content=system_message), HumanMessage(content=user_input), response]
        state['current_step'] = 'requirements_analyzed'
        state['iteration_count'] = state.get('iteration_count', 0) + 1
        
        logger.info("요구사항 분석 완료")
        return state
    
    async def _search_knowledge(self, state: PartyPlanState) -> PartyPlanState:
        """지식 검색 노드 (RAG + MCP)"""
        logger.info("관련 지식 검색 시작")
        
        party_type = state['party_type']
        guest_count = state['guest_count']
        budget = state.get('budget')
        location = state.get('location', '서울')
        
        # MCP를 통한 실시간 정보 수집
        try:
            # 장소 검색
            venue_result = await self.mcp_client.call_tool(
                "party_planning", 
                "search_venues",
                {
                    "location": location,
                    "capacity": guest_count,
                    "budget_max": float(budget) if budget else None
                }
            )
            
            # 케이터링 옵션 검색
            catering_result = await self.mcp_client.call_tool(
                "party_planning",
                "get_catering_options", 
                {
                    "guest_count": guest_count,
                    "budget_per_person": float(budget) / guest_count if budget else None,
                    "dietary_restrictions": state.get('dietary_restrictions', [])
                }
            )
            
            # 예산 계산
            budget_result = await self.mcp_client.call_tool(
                "party_planning",
                "calculate_budget",
                {
                    "party_type": party_type,
                    "guest_count": guest_count
                }
            )
            
            # 검색 결과를 컨텍스트로 구성
            context_info = f"""
            == MCP 도구를 통한 실시간 정보 ==
            
            추천 장소:
            {json.dumps(venue_result, ensure_ascii=False, indent=2)}
            
            케이터링 옵션:
            {json.dumps(catering_result, ensure_ascii=False, indent=2)}
            
            예산 계산:
            {json.dumps(budget_result, ensure_ascii=False, indent=2)}
            
            == 기본 파티 플래닝 가이드 ==
            
            {party_type} 파티 추천사항:
            - 생일파티: 케이크, 촛불, 생일축하 노래, 선물 교환, 게임
            - 결혼기념일: 로맨틱한 분위기, 꽃 장식, 기념품, 사진 촬영
            - 회사파티: 팀빌딩, 네트워킹, 뷔페식 식사, 시상식
            - 졸업파티: 기념품, 사진 부스, 축하 메시지
            
            인원수별 장소 추천:
            - 10명 이하: 카페, 집, 작은 레스토랑
            - 10-30명: 파티룸, 레스토랑 별실
            - 30-50명: 호텔 연회장, 커뮤니티 센터
            - 50명 이상: 대형 연회장, 야외 공간
            """
            
        except Exception as e:
            logger.warning(f"MCP 도구 호출 실패: {e}, 기본 정보를 사용합니다.")
            # MCP 실패 시 기본 컨텍스트 사용
            context_info = f"""
            == 파티 플래닝 가이드 ==
            
            {party_type} 파티 추천사항:
            - 생일파티: 케이크, 촛불, 생일축하 노래, 선물 교환, 게임
            - 결혼기념일: 로맨틱한 분위기, 꽃 장식, 기념품, 사진 촬영
            - 회사파티: 팀빌딩, 네트워킹, 뷔페식 식사, 시상식
            - 졸업파티: 기념품, 사진 부스, 축하 메시지
            
            인원수별 장소 추천:
            - 10명 이하: 카페, 집, 작은 레스토랑
            - 10-30명: 파티룸, 레스토랑 별실
            - 30-50명: 호텔 연회장, 커뮤니티 센터
            - 50명 이상: 대형 연회장, 야외 공간
            
            예산별 가이드:
            - 10만원 이하: 집에서 간단한 파티
            - 10-50만원: 카페나 레스토랑 파티
            - 50-100만원: 호텔이나 파티룸 이용
            - 100만원 이상: 풀서비스 파티
            """
        
        state['rag_context'] = context_info
        state['current_step'] = 'knowledge_searched'
        
        logger.info("관련 지식 검색 완료")
        return state
    
    async def _generate_plan(self, state: PartyPlanState) -> PartyPlanState:
        """전체 계획 생성 노드"""
        logger.info("파티 계획 생성 시작")
        
        system_message = """당신은 전문 파티 플래너입니다. 
        고객의 요구사항과 관련 지식을 바탕으로 구체적이고 실행 가능한 파티 계획을 생성해주세요.
        
        계획에 포함할 내용:
        1. 파티의 전체적인 컨셉과 분위기
        2. 추천 장소와 그 이유
        3. 음식/음료 계획
        4. 장식 및 분위기 연출
        5. 활동 및 프로그램
        6. 주의사항 및 팁
        
        실용적이고 구체적인 제안을 해주세요."""
        
        # 이전 분석 결과와 컨텍스트 정보 결합
        user_message = f"""
        이전 분석 결과:
        {state['messages'][-1].content if state['messages'] else ''}
        
        참고 정보:
        {state.get('rag_context', '')}
        
        위 정보를 바탕으로 {state['party_type']} 파티의 전체 계획을 생성해주세요.
        """
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        state['overall_plan'] = response.content
        state['messages'].extend([SystemMessage(content=system_message), HumanMessage(content=user_message), response])
        state['current_step'] = 'plan_generated'
        
        logger.info("파티 계획 생성 완료")
        return state
    
    def _create_tasks(self, state: PartyPlanState) -> PartyPlanState:
        """할일 목록 생성 노드"""
        logger.info("할일 목록 생성 시작")
        
        system_message = """생성된 파티 계획을 바탕으로 구체적인 할일 목록을 만들어주세요.
        각 할일은 다음 형식으로 JSON 배열로 반환해주세요:
        
        [
            {
                "task": "할일 제목",
                "description": "상세 설명",
                "priority": "high/medium/low",
                "deadline": "마감일 (D-day 형식)",
                "estimated_time": "예상 소요시간",
                "responsible": "담당자 (본인/업체/기타)"
            }
        ]
        
        파티 날짜 기준으로 우선순위와 마감일을 설정해주세요."""
        
        party_date = state['date']
        user_message = f"""
        파티 계획:
        {state['overall_plan']}
        
        파티 날짜: {party_date.strftime('%Y년 %m월 %d일')}
        
        위 계획을 실행하기 위한 구체적인 할일 목록을 생성해주세요.
        """
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ]
        
        response = self.llm.invoke(messages)
        
        # JSON 파싱 시도
        try:
            # 응답에서 JSON 부분 추출
            content = response.content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            elif "[" in content and "]" in content:
                json_start = content.find("[")
                json_end = content.rfind("]") + 1
                json_content = content[json_start:json_end]
            else:
                json_content = content
            
            tasks = json.loads(json_content)
            state['tasks'] = tasks
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 작업 목록 생성
            state['tasks'] = [
                {
                    "task": "장소 예약",
                    "description": "파티 장소를 예약하고 확정합니다",
                    "priority": "high",
                    "deadline": "D-14",
                    "estimated_time": "2시간",
                    "responsible": "본인"
                },
                {
                    "task": "음식 주문",
                    "description": "케이터링 또는 음식을 주문합니다",
                    "priority": "high", 
                    "deadline": "D-7",
                    "estimated_time": "1시간",
                    "responsible": "본인"
                },
                {
                    "task": "장식 준비",
                    "description": "파티 장식을 구매하고 준비합니다",
                    "priority": "medium",
                    "deadline": "D-3",
                    "estimated_time": "3시간",
                    "responsible": "본인"
                }
            ]
        
        state['current_step'] = 'tasks_created'
        
        logger.info("할일 목록 생성 완료")
        return state
    
    async def _estimate_costs(self, state: PartyPlanState) -> PartyPlanState:
        """비용 추정 노드"""
        logger.info("비용 추정 시작")
        
        guest_count = state['guest_count']
        party_type = state['party_type']
        
        # 기본 비용 추정 로직
        base_cost_per_person = {
            '생일파티': 25000,
            '결혼기념일': 60000,
            '회사파티': 45000,
            '졸업파티': 20000,
            '기타': 30000
        }
        
        per_person_cost = base_cost_per_person.get(party_type, 30000)
        base_cost = per_person_cost * guest_count
        
        # 장소비 추가 (인원수에 따라)
        if guest_count <= 10:
            venue_cost = 100000
        elif guest_count <= 30:
            venue_cost = 300000
        elif guest_count <= 50:
            venue_cost = 500000
        else:
            venue_cost = 1000000
        
        total_estimated_cost = base_cost + venue_cost
        
        # 사용자 예산과 비교
        user_budget = state.get('budget')
        if user_budget and total_estimated_cost > user_budget:
            # 예산 초과 시 조정 제안
            total_estimated_cost = user_budget
        
        state['estimated_cost'] = Decimal(str(total_estimated_cost))
        state['current_step'] = 'costs_estimated'
        
        logger.info(f"비용 추정 완료: {total_estimated_cost:,}원")
        return state
    
    def _create_timeline(self, state: PartyPlanState) -> PartyPlanState:
        """타임라인 생성 노드"""
        logger.info("타임라인 생성 시작")
        
        party_date = state['date']
        # timezone aware datetime으로 변환
        if party_date.tzinfo is None:
            from django.utils import timezone
            party_date = timezone.make_aware(party_date)
        
        today = datetime.now()
        if today.tzinfo is None:
            from django.utils import timezone
            today = timezone.make_aware(today)
            
        days_until_party = (party_date - today).days
        
        # 기본 타임라인 생성
        timeline = []
        
        # D-14: 계획 수립 및 장소 예약
        if days_until_party >= 14:
            timeline.append({
                "date": (party_date - timedelta(days=14)).strftime('%Y-%m-%d'),
                "day_description": "D-14",
                "tasks": ["계획 최종 확정", "장소 예약", "초대장 발송 준비"],
                "priority": "high"
            })
        
        # D-7: 음식 주문 및 상세 준비
        if days_until_party >= 7:
            timeline.append({
                "date": (party_date - timedelta(days=7)).strftime('%Y-%m-%d'),
                "day_description": "D-7",
                "tasks": ["음식/케이터링 주문", "참석자 최종 확인", "장식 구매"],
                "priority": "high"
            })
        
        # D-3: 마지막 준비
        if days_until_party >= 3:
            timeline.append({
                "date": (party_date - timedelta(days=3)).strftime('%Y-%m-%d'),
                "day_description": "D-3",
                "tasks": ["장소 최종 점검", "장식 설치 준비", "음식 픽업/배송 확인"],
                "priority": "medium"
            })
        
        # D-1: 당일 직전 준비
        if days_until_party >= 1:
            timeline.append({
                "date": (party_date - timedelta(days=1)).strftime('%Y-%m-%d'),
                "day_description": "D-1",
                "tasks": ["장식 설치", "음식 최종 준비", "장소 셋업"],
                "priority": "high"
            })
        
        # D-Day: 파티 당일
        timeline.append({
            "date": party_date.strftime('%Y-%m-%d'),
            "day_description": "D-Day",
            "tasks": ["최종 셋업 확인", "파티 진행", "정리 및 뒷정리"],
            "priority": "critical"
        })
        
        state['timeline'] = timeline
        state['current_step'] = 'timeline_created'
        
        logger.info("타임라인 생성 완료")
        return state
    
    async def _finalize_plan(self, state: PartyPlanState) -> PartyPlanState:
        """계획 최종화 노드"""
        logger.info("계획 최종화 시작")
        
        # 추천사항 생성
        recommendations = [
            {
                "category": "예산 절약",
                "suggestion": "직접 준비할 수 있는 부분은 DIY로 비용을 절약하세요",
                "priority": "medium"
            },
            {
                "category": "성공 팁",
                "suggestion": "파티 2주 전부터 단계별로 준비하면 스트레스를 줄일 수 있습니다",
                "priority": "high"
            },
            {
                "category": "비상 계획",
                "suggestion": "날씨나 기타 변수에 대비한 Plan B를 준비해두세요",
                "priority": "medium"
            }
        ]
        
        # 특별 요구사항에 따른 추가 추천
        if state.get('dietary_restrictions'):
            recommendations.append({
                "category": "식단 관리",
                "suggestion": f"식단 제한사항({', '.join(state['dietary_restrictions'])})을 고려한 메뉴를 꼭 준비하세요",
                "priority": "high"
            })
        
        state['recommendations'] = recommendations
        state['plan_id'] = str(uuid.uuid4())
        state['current_step'] = 'plan_finalized'
        
        logger.info("계획 최종화 완료")
        return state
    
    async def create_party_plan(self, party_request: Dict) -> Dict:
        """파티 계획 생성 메인 함수"""
        try:
            # 입력 데이터 준비
            initial_state = PartyPlanState(
                party_type=party_request['party_type'],
                budget=party_request.get('budget'),
                guest_count=party_request['guest_count'],
                date=party_request['date'],
                location=party_request.get('location'),
                special_requirements=party_request.get('special_requirements'),
                dietary_restrictions=party_request.get('dietary_restrictions', []),
                messages=[],
                plan_id="",
                overall_plan="",
                tasks=[],
                estimated_cost=None,
                timeline=[],
                recommendations=[],
                current_step="starting",
                rag_context="",
                iteration_count=0
            )
            
            # LangGraph 실행
            result = await self.graph.ainvoke(initial_state)
            
            # 결과 포맷팅
            return {
                'plan_id': result['plan_id'],
                'overall_plan': result['overall_plan'],
                'tasks': result['tasks'],
                'estimated_cost': float(result['estimated_cost']) if result['estimated_cost'] else None,
                'timeline': result['timeline'],
                'recommendations': result['recommendations']
            }
            
        except Exception as e:
            logger.error(f"파티 계획 생성 오류: {e}")
            raise e