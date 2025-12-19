#!/bin/bash
# 로컬 로그인 API 테스트 스크립트

echo "======================================"
echo "로그인 API 테스트"
echo "======================================"
echo ""

# 테스트할 이메일과 비밀번호
read -p "Email: " EMAIL
read -sp "Password: " PASSWORD
echo ""
echo ""

echo "요청 전송 중..."
echo ""

# POST 요청 전송
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  -w "\n\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  -v

echo ""
echo "======================================"
