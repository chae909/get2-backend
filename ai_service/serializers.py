# ai_service/serializers.py

from rest_framework import serializers

class AIQuerySerializer(serializers.Serializer):
    """AI 쿼리 요청 시리얼라이저"""
    question = serializers.CharField(max_length=2000, required=True)
    session_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    context = serializers.DictField(required=False, allow_empty=True)

class AIResponseSerializer(serializers.Serializer):
    """AI 응답 시리얼라이저"""
    answer = serializers.CharField()
    session_id = serializers.CharField()
    confidence = serializers.FloatField(required=False)
    sources = serializers.ListField(child=serializers.DictField(), required=False)

class PartyPlanningRequestSerializer(serializers.Serializer):
    """파티 플래닝 요청 시리얼라이저"""
    party_type = serializers.CharField(max_length=100, required=True)
    budget = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    guest_count = serializers.IntegerField(required=True)
    date = serializers.DateTimeField(required=True)
    location = serializers.CharField(max_length=500, required=False)
    special_requirements = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )

class PartyPlanResponseSerializer(serializers.Serializer):
    """파티 플래닝 응답 시리얼라이저"""
    plan_id = serializers.CharField()
    overall_plan = serializers.CharField()
    tasks = serializers.ListField(child=serializers.DictField())
    estimated_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    timeline = serializers.ListField(child=serializers.DictField())
    recommendations = serializers.ListField(child=serializers.DictField())