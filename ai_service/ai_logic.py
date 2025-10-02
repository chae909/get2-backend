# ai_service/ai_logic.py

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain.schema import SystemMessage, HumanMessage

# .env 파일에서 API 키를 불러옵니다.
load_dotenv()

# 1. AI 모델 준비
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. 대화 상태를 저장할 데이터 구조 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: Dict[str, Any]

# 3. AI 그래프 빌더 설정
graph_builder = StateGraph(State)

# 4. 향상된 AI 응답 함수
def call_model_with_context(state: State):
    """컨텍스트를 고려한 AI 모델 호출"""
    messages = state['messages']
    context = state.get('context', {})
    
    # 시스템 메시지에 컨텍스트 정보 추가
    system_prompt = """당신은 도움이 되는 AI 어시스턴트입니다. 
    사용자의 질문에 정확하고 유용한 답변을 제공해주세요.
    
    필요한 경우 다음과 같은 형태로 응답해주세요:
    - 명확하고 구체적인 답변
    - 단계별 설명 (필요시)
    - 추가 도움이 될 만한 정보나 팁
    """
    
    # 컨텍스트가 있는 경우 시스템 프롬프트에 추가
    if context:
        context_info = "\n\n추가 컨텍스트 정보:\n"
        for key, value in context.items():
            context_info += f"- {key}: {value}\n"
        system_prompt += context_info
    
    # 메시지 리스트 준비
    if not messages or not isinstance(messages[0], SystemMessage):
        full_messages = [SystemMessage(content=system_prompt)] + messages
    else:
        full_messages = messages
    
    response = llm.invoke(full_messages)
    return {"messages": [response]}

# 5. 그래프에 노드 추가 및 설정
graph_builder.add_node("llm", call_model_with_context)
graph_builder.set_entry_point("llm")
graph_builder.set_finish_point("llm")

# 6. 그래프 컴파일
chain = graph_builder.compile()

# 7. 향상된 비동기 함수
async def get_ai_response(user_question: str, context: Dict[str, Any] = None) -> str:
    """
    사용자 질문에 대한 AI 응답 생성
    
    Args:
        user_question: 사용자의 질문
        context: 추가 컨텍스트 정보 (선택사항)
    
    Returns:
        AI 응답 텍스트
    """
    try:
        if context is None:
            context = {}
            
        result = await chain.ainvoke({
            "messages": [HumanMessage(content=user_question)],
            "context": context
        })
        
        return result['messages'][-1].content
        
    except Exception as e:
        return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"

# 8. 특별한 기능들을 위한 헬퍼 함수들
async def get_party_planning_response(question: str, party_context: Dict = None) -> str:
    """파티 플래닝 관련 질문을 위한 특화된 응답"""
    context = {
        "domain": "party_planning",
        "expertise": "이벤트 기획, 파티 조직, 예산 관리"
    }
    
    if party_context:
        context.update(party_context)
    
    enhanced_question = f"""
    파티 플래닝 관련 질문: {question}
    
    다음 관점에서 답변해주세요:
    1. 실용적이고 실행 가능한 조언
    2. 예산 고려사항
    3. 시간 관리 팁
    4. 주의사항이나 체크리스트
    """
    
    return await get_ai_response(enhanced_question, context)