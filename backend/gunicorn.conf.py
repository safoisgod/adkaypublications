"""
Gunicorn configuration for production deployment.
Run: gunicorn -c gunicorn.conf.py config.wsgi:application
"""
import multiprocessing
import os

# ── Server socket ─────────────────────────────────────────────────────────────
bind = "127.0.0.1:8000"
backlog = 2048

# ── Worker processes ──────────────────────────────────────────────────────────
# Formula: (2 * CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

# ── Logging ───────────────────────────────────────────────────────────────────
loglevel = "info"
accesslog = "/var/log/gunicorn/publishing_access.log"
errorlog = "/var/log/gunicorn/publishing_error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ── Process naming ────────────────────────────────────────────────────────────
proc_name = "publishing_house"

# ── Security ──────────────────────────────────────────────────────────────────
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# ── Django settings ───────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

def on_starting(server):
    server.log.info("Publishing House API starting...")

def on_exit(server):
    server.log.info("Publishing House API shutting down.")

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited.")
