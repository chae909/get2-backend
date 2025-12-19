"""Gunicorn configuration for Django/ASGI application"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 3))  # Render에서는 3개가 안전
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
timeout = 120  # 2분으로 설정
keepalive = 5
graceful_timeout = 30

# Restart workers after this many requests (helps prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'get2-backend'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app - False로 설정하여 worker마다 독립적으로 로드
# (Supabase 클라이언트 초기화 문제 방지)
preload_app = False

# Worker가 제대로 시작되었는지 확인
def on_starting(server):
    print(f"Gunicorn starting with bind={bind}, workers={workers}")

def when_ready(server):
    print(f"Gunicorn ready to accept connections")

def worker_int(worker):
    print(f"Worker {worker.pid} received INT or QUIT signal")

# SSL (if needed)
# keyfile = None
# certfile = None
