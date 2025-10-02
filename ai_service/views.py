# ai_service/views.py

import json
import uuid
import asyncio
from asgiref.sync import sync_to_async
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from .serializers import (
    AIQuerySerializer, 
    AIResponseSerializer,
    PartyPlanningRequestSerializer,
    PartyPlanResponseSerializer
)
from .ai_logic import get_ai_response
from .party_planning_agent import PartyPlanningAgent

class BaseAIView(View):
    """AI 서비스 기본 뷰 클래스"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([AllowAny])
def ask_ai(request):
    """일반 AI 질답 엔드포인트"""
    serializer = AIQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid request data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        question = serializer.validated_data['question']
        session_id = serializer.validated_data.get('session_id', str(uuid.uuid4()))
        context = serializer.validated_data.get('context', {})
        
        # AI 응답 생성 (비동기를 동기로 변환)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ai_answer = loop.run_until_complete(get_ai_response(question, context))
        finally:
            loop.close()
        
        response_data = {
            'answer': ai_answer,
            'session_id': session_id,
            'confidence': 0.95  # 임시값, 실제로는 모델에서 계산
        }
        
        response_serializer = AIResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'서버 내부 오류: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def plan_party(request):
    """파티 플래닝 전용 AI 엔드포인트"""
    serializer = PartyPlanningRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid request data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 파티 플래닝 에이전트 인스턴스 생성
        agent = PartyPlanningAgent()
        
        # 파티 플래닝 실행 (비동기를 동기로 변환)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            plan_result = loop.run_until_complete(agent.create_party_plan(serializer.validated_data))
        finally:
            loop.close()
        
        response_serializer = PartyPlanResponseSerializer(data=plan_result)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response(plan_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'파티 플래닝 오류: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """AI 서비스 상태 확인"""
    return Response({
        'status': 'healthy',
        'service': 'AI Party Planning Service',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)