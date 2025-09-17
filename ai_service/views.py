# ai_service/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_logic import get_ai_response # 3단계에서 만든 AI 함수를 가져옵니다.

# Django 4.1부터 비동기 뷰를 정식 지원합니다.
# @csrf_exempt는 테스트를 위해 잠시 CSRF 보호를 끄는 데코레이터입니다.
# 실제 서비스에서는 적절한 CSRF 처리가 필요합니다!
@csrf_exempt
async def ask_ai(request):
    if request.method == 'POST':
        try:
            # 손님(프론트엔드)이 보낸 데이터를 JSON 형태로 받습니다.
            data = json.loads(request.body)
            question = data.get('question')

            if not question:
                return JsonResponse({'error': '질문이 없습니다.'}, status=400)

            # AI 로봇 셰프에게 요리를 요청하고 답변을 기다립니다. (await)
            ai_answer = await get_ai_response(question)

            # 완성된 요리(답변)를 손님에게 전달합니다.
            return JsonResponse({'answer': ai_answer})

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 형식의 요청입니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'서버 내부 오류: {e}'}, status=500)

    return JsonResponse({'error': 'POST 요청만 지원합니다.'}, status=405)