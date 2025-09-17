# ai_service/ai_logic.py

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

# .env 파일에서 API 키를 불러옵니다.
load_dotenv()

# 1. AI 셰프(모델) 준비
# 온도(temperature)는 창의성 조절, 0에 가까울수록 정해진 답변만 합니다.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 대화 상태를 저장할 데이터 구조 정의
# LangGraph는 '상태(State)'를 계속 업데이트하며 작업을 진행합니다.
# 우리 레스토랑의 '주문서'와 같습니다.
class State(TypedDict):
    # `add_messages`는 새로운 메시지가 들어오면 기존 대화에 계속 추가해주는 역할을 합니다.
    messages: Annotated[list, add_messages]

# 3. AI 로봇 셰프의 작업 순서(그래프) 설계
graph_builder = StateGraph(State)

# 4. '요리하기' 단계(노드) 정의
# 이 함수가 AI 셰프의 핵심 동작입니다.
def call_model(state: State):
    # 현재까지의 대화(주문서)를 AI 셰프에게 보여주고
    messages = state['messages']
    # 다음 할 말을 생성해달라고 요청합니다.
    response = llm.invoke(messages)
    # 생성된 답변을 주문서(상태)에 추가해서 반환합니다.
    return {"messages": [response]}

# 5. 작업 순서에 '요리하기' 단계 추가 및 시작점/종점 설정
graph_builder.add_node("llm", call_model) # 'llm'이라는 이름의 작업 단계를 추가
graph_builder.set_entry_point("llm") # 'llm' 단계에서 작업을 시작
graph_builder.set_finish_point("llm") # 'llm' 단계에서 작업을 종료 (간단한 예제라서 시작과 끝이 같습니다)

# 6. 완성된 AI 작업 흐름(레시피) 컴파일
# 이제 이 'chain' 객체를 호출하면 AI가 동작합니다.
chain = graph_builder.compile()

# 7. 장고에서 호출할 비동기 함수 만들기
# 이 함수가 장고와 랭그래프를 연결하는 '다리' 역할을 합니다.
async def get_ai_response(user_question: str):
    # AI는 작업 시간이 길 수 있으므로 비동기(async)로 처리하는 것이 좋습니다.
    # 웹 서버가 AI의 답변을 기다리는 동안 멈추는 것을 방지해줍니다.
    result = await chain.ainvoke({
        "messages": [("human", user_question)]
    })
    # AI가 생성한 마지막 메시지(답변)의 내용만 추출하여 반환합니다.
    return result['messages'][-1].content