"""Gunicorn configuration for Django/ASGI application"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes - 무료 플랜(512MB)에서는 1개만 사용
# 유료 플랜에서는 WEB_CONCURRENCY 환경변수로 조절 가능
workers = int(os.environ.get('WEB_CONCURRENCY', 1))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 100  # 메모리 절약을 위해 감소
timeout = 120
keepalive = 5
graceful_timeout = 30

# 메모리 누수 방지 - 더 자주 재시작
max_requests = 500
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

# Worker마다 독립적으로 로드
preload_app = False

# 디버깅 로그
def on_starting(server):
    print(f"Gunicorn starting with bind={bind}, workers={workers}")

def when_ready(server):
    print(f"Gunicorn ready to accept connections")

def worker_int(worker):
    print(f"Worker {worker.pid} received INT or QUIT signal")

def post_worker_init(worker):
    print(f"Worker {worker.pid} initialized")

# SSL (if needed)
# keyfile = None
# certfile = None
