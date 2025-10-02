# Party Planning AI Agent API 사용 가이드

## 개요

Django 기반의 파티 플래닝 AI 에이전트가 성공적으로 구현되었습니다. 이 시스템은 다음과 같은 핵심 기능을 제공합니다:

### 🌟 주요 기능
- **LangGraph 기반 AI 에이전트**: 복잡한 파티 플래닝 워크플로우 처리
- **RAG (Retrieval-Augmented Generation)**: 파티 관련 지식 데이터베이스 활용
- **MCP (Model Context Protocol)**: 실시간 정보 검색 및 외부 도구 통합
- **RESTful API**: 프론트엔드와의 원활한 통신

## 📁 구현된 파일 구조

```
ai_service/
├── __init__.py
├── admin.py
├── ai_logic.py              # 기본 AI 로직 및 LangGraph 설정
├── apps.py
├── models.py
├── mcp_integration.py       # MCP 통합 및 외부 도구 연결
├── party_planning_agent.py  # 파티 플래닝 전용 AI 에이전트
├── rag_system.py           # 검색 증강 시스템 (RAG)
├── serializers.py          # API 직렬화
├── tests.py
├── urls.py                 # API 엔드포인트 라우팅
└── views.py                # API 뷰 함수들
```

## 🚀 API 엔드포인트

### 1. 일반 AI 질답
**POST** `/api/v1/ai/ask/`

```json
{
  "question": "파티 준비에 대해 조언해주세요",
  "session_id": "optional-session-id",
  "context": {
    "domain": "party_planning"
  }
}
```

**응답:**
```json
{
  "answer": "AI가 생성한 답변",
  "session_id": "session-id",
  "confidence": 0.95
}
```

### 2. 파티 플래닝 (메인 기능)
**POST** `/api/v1/ai/party/plan/`

```json
{
  "party_type": "생일파티",
  "budget": 500000,
  "guest_count": 20,
  "date": "2025-03-15T18:00:00Z",
  "location": "강남구",
  "special_requirements": "야외 파티 선호",
  "dietary_restrictions": ["vegetarian", "gluten_free"]
}
```

**응답:**
```json
{
  "plan_id": "uuid-generated-id",
  "overall_plan": "상세한 파티 계획서...",
  "tasks": [
    {
      "task": "장소 예약",
      "description": "파티 장소를 예약하고 확정합니다",
      "priority": "high",
      "deadline": "D-14",
      "estimated_time": "2시간",
      "responsible": "본인"
    }
  ],
  "estimated_cost": 450000.00,
  "timeline": [
    {
      "date": "2025-03-01",
      "day_description": "D-14",
      "tasks": ["계획 최종 확정", "장소 예약"],
      "priority": "high"
    }
  ],
  "recommendations": [
    {
      "category": "예산 절약",
      "suggestion": "직접 준비할 수 있는 부분은 DIY로 비용을 절약하세요",
      "priority": "medium"
    }
  ]
}
```

### 3. 서비스 상태 확인
**GET** `/api/v1/ai/health/`

```json
{
  "status": "healthy",
  "service": "AI Party Planning Service",
  "version": "1.0.0"
}
```

## 🧠 AI 에이전트 워크플로우

### LangGraph 노드 구조:
1. **요구사항 분석** (`analyze_requirements`)
   - 사용자 입력 분석
   - 파티의 핵심 포인트 파악

2. **지식 검색** (`search_knowledge`)
   - RAG 시스템으로 관련 정보 검색
   - MCP 도구로 실시간 정보 수집

3. **계획 생성** (`generate_plan`)
   - 전체적인 파티 컨셉 수립
   - 장소, 음식, 활동 계획

4. **할일 목록 생성** (`create_tasks`)
   - 구체적인 실행 단계 계획
   - 우선순위 및 마감일 설정

5. **비용 추정** (`estimate_costs`)
   - 예산 계산 및 비용 분석
   - 사용자 예산과 비교

6. **타임라인 생성** (`create_timeline`)
   - 파티 준비 일정 수립
   - D-day 기준 단계별 계획

7. **계획 최종화** (`finalize_plan`)
   - 추천사항 생성
   - 최종 검토 및 정리

## 🔧 MCP 통합 도구

### 사용 가능한 MCP 도구:
1. **search_venues**: 지역별 파티 장소 검색
2. **get_catering_options**: 케이터링 옵션 검색
3. **check_weather**: 날씨 확인 (야외 파티용)
4. **calculate_budget**: 예산 계산
5. **generate_timeline**: 준비 타임라인 생성

### MCP 리소스:
- 파티 장소 데이터베이스
- 케이터링 메뉴 정보
- 장식 카탈로그

## 📊 RAG 시스템 특징

### 벡터 데이터베이스 컬렉션:
- **party_ideas**: 파티 아이디어 및 추천사항
- **venues**: 장소 정보
- **catering**: 케이터링 옵션
- **decorations**: 장식 아이디어
- **activities**: 파티 활동

### 검색 기능:
- 의미론적 유사도 검색
- 컨텍스트 기반 정보 검색
- 실시간 지식 업데이트

## 🛠️ 환경 설정

### 필수 환경 변수:
```env
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
DB_PORT=5432
```

### 패키지 의존성:
- `langchain>=0.3.27`
- `langchain-openai>=0.2.5`
- `langgraph>=0.6.7`
- `chromadb>=0.5.0`
- `sentence-transformers>=3.0.0`
- `djangorestframework>=3.16.1`

## 📈 사용 예시

### 1. 간단한 생일파티 계획:
```python
import requests

response = requests.post('http://localhost:8000/api/v1/ai/party/plan/', json={
    "party_type": "생일파티",
    "guest_count": 15,
    "date": "2025-04-20T15:00:00Z",
    "budget": 300000,
    "location": "홍대"
})

plan = response.json()
print(f"계획 ID: {plan['plan_id']}")
print(f"예상 비용: {plan['estimated_cost']:,}원")
```

### 2. 회사 파티 계획:
```python
response = requests.post('http://localhost:8000/api/v1/ai/party/plan/', json={
    "party_type": "회사파티",
    "guest_count": 50,
    "date": "2025-05-10T18:30:00Z",
    "budget": 1000000,
    "special_requirements": "팀빌딩 활동 포함",
    "dietary_restrictions": ["halal", "vegetarian"]
})
```

## 🔄 확장 가능성

### 향후 개선 사항:
1. **실제 업체 API 연동**: 실시간 가격 및 가용성 확인
2. **예약 시스템 통합**: 직접 예약 기능
3. **사용자 피드백 학습**: 추천 시스템 개선
4. **다국어 지원**: 국제 파티 플래닝
5. **모바일 최적화**: PWA 지원

### 추가 MCP 도구:
- 소셜미디어 초대장 생성
- 음악 플레이리스트 추천
- 포토부스 예약
- 선물 추천 시스템

## 🚀 배포 및 운영

### 개발 서버 실행:
```bash
# 의존성 설치
uv sync

# 마이그레이션 실행
python manage.py migrate

# 서버 시작
python manage.py runserver
```

### 프로덕션 설정:
- Gunicorn 또는 uWSGI 사용
- Redis/Celery로 비동기 작업 처리
- PostgreSQL 데이터베이스
- Docker 컨테이너화

## 💡 사용 팁

1. **예산 최적화**: 예산 범위를 명확히 설정하면 더 정확한 추천을 받을 수 있습니다.
2. **특별 요구사항**: 구체적인 요구사항을 제공할수록 맞춤형 계획을 받을 수 있습니다.
3. **준비 기간**: 파티 날짜까지 충분한 시간을 두면 더 다양한 옵션을 제공받을 수 있습니다.
4. **피드백 활용**: 생성된 계획에 대한 피드백을 통해 시스템이 학습합니다.

이 파티 플래닝 AI 에이전트는 사용자의 요구사항을 분석하여 개인화된 파티 계획을 제공하며, 실시간 정보 검색과 지식 데이터베이스를 통해 실용적이고 실행 가능한 조언을 제공합니다.