# ai_service/mcp_integration.py

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP 도구 정의"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]

@dataclass
class MCPResource:
    """MCP 리소스 정의"""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None

class MCPProvider(ABC):
    """MCP 프로바이더 추상 클래스"""
    
    @abstractmethod
    async def get_tools(self) -> List[MCPTool]:
        """사용 가능한 도구 목록 반환"""
        pass
    
    @abstractmethod
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """도구 호출"""
        pass
    
    @abstractmethod
    async def get_resources(self) -> List[MCPResource]:
        """사용 가능한 리소스 목록 반환"""
        pass
    
    @abstractmethod
    async def read_resource(self, uri: str) -> str:
        """리소스 읽기"""
        pass

class PartyPlanningMCPProvider(MCPProvider):
    """파티 플래닝을 위한 MCP 프로바이더"""
    
    def __init__(self):
        self.tools = [
            MCPTool(
                name="search_venues",
                description="특정 지역에서 파티 장소를 검색합니다",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "검색할 지역"},
                        "capacity": {"type": "integer", "description": "최소 수용 인원"},
                        "budget_max": {"type": "number", "description": "최대 예산"}
                    }
                },
                required=["location", "capacity"]
            ),
            MCPTool(
                name="get_catering_options",
                description="케이터링 옵션을 검색합니다",
                parameters={
                    "type": "object",
                    "properties": {
                        "cuisine_type": {"type": "string", "description": "음식 종류"},
                        "guest_count": {"type": "integer", "description": "참석자 수"},
                        "budget_per_person": {"type": "number", "description": "인당 예산"},
                        "dietary_restrictions": {"type": "array", "items": {"type": "string"}, "description": "식단 제한사항"}
                    }
                },
                required=["guest_count"]
            ),
            MCPTool(
                name="check_weather",
                description="특정 날짜의 날씨를 확인합니다 (야외 파티 계획용)",
                parameters={
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "날짜 (YYYY-MM-DD)"},
                        "location": {"type": "string", "description": "지역"}
                    }
                },
                required=["date", "location"]
            ),
            MCPTool(
                name="calculate_budget",
                description="파티 예산을 계산합니다",
                parameters={
                    "type": "object",
                    "properties": {
                        "party_type": {"type": "string", "description": "파티 종류"},
                        "guest_count": {"type": "integer", "description": "참석자 수"},
                        "venue_cost": {"type": "number", "description": "장소 비용"},
                        "catering_cost": {"type": "number", "description": "음식 비용"},
                        "decoration_cost": {"type": "number", "description": "장식 비용"}
                    }
                },
                required=["guest_count"]
            ),
            MCPTool(
                name="generate_timeline",
                description="파티 준비 타임라인을 생성합니다",
                parameters={
                    "type": "object",
                    "properties": {
                        "party_date": {"type": "string", "description": "파티 날짜 (YYYY-MM-DD)"},
                        "complexity": {"type": "string", "enum": ["simple", "moderate", "complex"], "description": "파티 복잡도"}
                    }
                },
                required=["party_date"]
            )
        ]
        
        self.resources = [
            MCPResource(
                uri="party://venues/database",
                name="Venue Database",
                description="파티 장소 데이터베이스",
                mime_type="application/json"
            ),
            MCPResource(
                uri="party://catering/menu",
                name="Catering Menu",
                description="케이터링 메뉴 정보",
                mime_type="application/json"
            ),
            MCPResource(
                uri="party://decorations/catalog",
                name="Decoration Catalog",
                description="장식 카탈로그",
                mime_type="application/json"
            )
        ]
    
    async def get_tools(self) -> List[MCPTool]:
        """사용 가능한 도구 목록 반환"""
        return self.tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """도구 호출 처리"""
        try:
            if name == "search_venues":
                return await self._search_venues(**arguments)
            elif name == "get_catering_options":
                return await self._get_catering_options(**arguments)
            elif name == "check_weather":
                return await self._check_weather(**arguments)
            elif name == "calculate_budget":
                return await self._calculate_budget(**arguments)
            elif name == "generate_timeline":
                return await self._generate_timeline(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Tool call error ({name}): {e}")
            return {"error": str(e)}
    
    async def get_resources(self) -> List[MCPResource]:
        """사용 가능한 리소스 목록 반환"""
        return self.resources
    
    async def read_resource(self, uri: str) -> str:
        """리소스 읽기"""
        if uri == "party://venues/database":
            return json.dumps({
                "venues": [
                    {
                        "name": "그랜드 호텔 연회장",
                        "location": "강남구",
                        "capacity": 200,
                        "price_per_hour": 500000,
                        "amenities": ["음향시설", "주차장", "케이터링 서비스"]
                    },
                    {
                        "name": "카페 블루문",
                        "location": "홍대",
                        "capacity": 30,
                        "price_per_hour": 100000,
                        "amenities": ["음향시설", "프로젝터"]
                    }
                ]
            })
        elif uri == "party://catering/menu":
            return json.dumps({
                "catering_options": [
                    {
                        "name": "한식 뷔페",
                        "price_per_person": 25000,
                        "cuisine": "korean",
                        "dietary_options": ["vegetarian", "halal"]
                    },
                    {
                        "name": "양식 코스",
                        "price_per_person": 45000,
                        "cuisine": "western",
                        "dietary_options": ["vegetarian", "vegan", "gluten_free"]
                    }
                ]
            })
        else:
            return json.dumps({"error": "Resource not found"})
    
    async def _search_venues(self, location: str, capacity: int, budget_max: Optional[float] = None) -> Dict:
        """장소 검색 구현"""
        # 실제로는 외부 API나 데이터베이스를 조회
        venues = [
            {
                "name": f"{location} 파티룸 A",
                "location": location,
                "capacity": capacity + 10,
                "hourly_rate": min(budget_max or 300000, 200000),
                "rating": 4.5,
                "amenities": ["음향시설", "주차장", "케이터링 지원"]
            },
            {
                "name": f"{location} 커뮤니티 센터",
                "location": location,
                "capacity": capacity + 20,
                "hourly_rate": min(budget_max or 300000, 150000),
                "rating": 4.2,
                "amenities": ["넓은 공간", "주차장", "주방시설"]
            }
        ]
        
        if budget_max:
            venues = [v for v in venues if v["hourly_rate"] <= budget_max]
        
        return {"venues": venues}
    
    async def _get_catering_options(self, guest_count: int, cuisine_type: Optional[str] = None,
                                  budget_per_person: Optional[float] = None,
                                  dietary_restrictions: Optional[List[str]] = None) -> Dict:
        """케이터링 옵션 검색"""
        options = [
            {
                "name": "프리미엄 뷔페",
                "price_per_person": 35000,
                "cuisine": "international",
                "dietary_options": ["vegetarian", "halal"],
                "minimum_order": 20
            },
            {
                "name": "간편 도시락",
                "price_per_person": 15000,
                "cuisine": "korean",
                "dietary_options": ["vegetarian"],
                "minimum_order": 10
            },
            {
                "name": "파티 플래터",
                "price_per_person": 25000,
                "cuisine": "western",
                "dietary_options": ["vegetarian", "vegan"],
                "minimum_order": 15
            }
        ]
        
        # 필터링
        if budget_per_person:
            options = [o for o in options if o["price_per_person"] <= budget_per_person]
        
        if cuisine_type:
            options = [o for o in options if o["cuisine"] == cuisine_type]
        
        if dietary_restrictions:
            options = [o for o in options if any(dr in o["dietary_options"] for dr in dietary_restrictions)]
        
        # 최소 주문량 확인
        options = [o for o in options if guest_count >= o["minimum_order"]]
        
        return {"catering_options": options}
    
    async def _check_weather(self, date: str, location: str) -> Dict:
        """날씨 확인 (모의 구현)"""
        # 실제로는 날씨 API를 호출
        return {
            "date": date,
            "location": location,
            "forecast": {
                "temperature": "22°C",
                "condition": "맑음",
                "precipitation": "10%",
                "wind": "약함",
                "recommendation": "야외 행사에 좋은 날씨입니다."
            }
        }
    
    async def _calculate_budget(self, guest_count: int, party_type: Optional[str] = None,
                              venue_cost: Optional[float] = None,
                              catering_cost: Optional[float] = None,
                              decoration_cost: Optional[float] = None) -> Dict:
        """예산 계산"""
        # 기본값 설정
        venue_cost = venue_cost or (guest_count * 5000)
        catering_cost = catering_cost or (guest_count * 25000)
        decoration_cost = decoration_cost or min(100000, guest_count * 2000)
        
        # 파티 타입별 조정
        multiplier = {
            "생일파티": 1.0,
            "결혼기념일": 1.5,
            "회사파티": 1.2,
            "졸업파티": 0.8
        }.get(party_type, 1.0)
        
        subtotal = (venue_cost + catering_cost + decoration_cost) * multiplier
        tax = subtotal * 0.1  # 10% 세금
        total = subtotal + tax
        
        return {
            "breakdown": {
                "venue": venue_cost * multiplier,
                "catering": catering_cost * multiplier,
                "decoration": decoration_cost * multiplier,
                "subtotal": subtotal,
                "tax": tax,
                "total": total
            },
            "per_person": total / guest_count
        }
    
    async def _generate_timeline(self, party_date: str, complexity: str = "moderate") -> Dict:
        """타임라인 생성"""
        timelines = {
            "simple": [
                {"weeks_before": 1, "task": "장소 예약 및 초대장 발송"},
                {"days_before": 3, "task": "음식 주문 및 장식 구매"},
                {"days_before": 1, "task": "최종 준비 및 셋업"}
            ],
            "moderate": [
                {"weeks_before": 3, "task": "예산 계획 및 컨셉 결정"},
                {"weeks_before": 2, "task": "장소 예약 및 케이터링 주문"},
                {"days_before": 10, "task": "초대장 발송"},
                {"days_before": 5, "task": "장식 및 용품 구매"},
                {"days_before": 2, "task": "최종 확인 및 준비"},
                {"days_before": 1, "task": "셋업 및 리허설"}
            ],
            "complex": [
                {"weeks_before": 6, "task": "전체 계획 수립 및 예산 설정"},
                {"weeks_before": 4, "task": "장소 예약 및 주요 업체 계약"},
                {"weeks_before": 3, "task": "초대장 제작 및 발송"},
                {"weeks_before": 2, "task": "세부 계획 확정 및 최종 주문"},
                {"days_before": 10, "task": "장식 준비 및 리허설 계획"},
                {"days_before": 5, "task": "최종 점검 및 조정"},
                {"days_before": 2, "task": "셋업 시작"},
                {"days_before": 1, "task": "최종 리허설 및 점검"}
            ]
        }
        
        return {
            "party_date": party_date,
            "complexity": complexity,
            "timeline": timelines.get(complexity, timelines["moderate"])
        }

class MCPClient:
    """MCP 클라이언트"""
    
    def __init__(self):
        self.providers: Dict[str, MCPProvider] = {}
        self.register_provider("party_planning", PartyPlanningMCPProvider())
    
    def register_provider(self, name: str, provider: MCPProvider):
        """MCP 프로바이더 등록"""
        self.providers[name] = provider
        logger.info(f"MCP provider '{name}' registered")
    
    async def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """모든 프로바이더의 도구 목록 반환"""
        all_tools = {}
        for name, provider in self.providers.items():
            all_tools[name] = await provider.get_tools()
        return all_tools
    
    async def call_tool(self, provider_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """특정 프로바이더의 도구 호출"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        provider = self.providers[provider_name]
        return await provider.call_tool(tool_name, arguments)
    
    async def get_contextual_tools(self, context: Dict[str, Any]) -> List[Dict]:
        """컨텍스트에 적합한 도구 추천"""
        recommended_tools = []
        
        # 파티 플래닝 컨텍스트 확인
        if context.get("domain") == "party_planning":
            party_provider = self.providers.get("party_planning")
            if party_provider:
                tools = await party_provider.get_tools()
                for tool in tools:
                    recommended_tools.append({
                        "provider": "party_planning",
                        "tool": tool,
                        "relevance_score": self._calculate_relevance(tool, context)
                    })
        
        # 관련성 점수로 정렬
        recommended_tools.sort(key=lambda x: x["relevance_score"], reverse=True)
        return recommended_tools
    
    def _calculate_relevance(self, tool: MCPTool, context: Dict[str, Any]) -> float:
        """도구와 컨텍스트의 관련성 점수 계산"""
        score = 0.5  # 기본 점수
        
        # 파티 관련 키워드 확인
        party_keywords = ["party", "venue", "catering", "budget", "timeline"]
        if any(keyword in tool.name.lower() or keyword in tool.description.lower() 
               for keyword in party_keywords):
            score += 0.3
        
        # 컨텍스트 매칭
        if context.get("guest_count") and "guest" in tool.description.lower():
            score += 0.2
        
        if context.get("budget") and "budget" in tool.name.lower():
            score += 0.2
        
        return min(score, 1.0)

# 전역 MCP 클라이언트 인스턴스
mcp_client = MCPClient()