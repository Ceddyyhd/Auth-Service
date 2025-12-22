# Gunicorn Configuration
# Location: /var/www/auth-service/gunicorn_config.py

import multiprocessing
import os

# Server Socket
bind = "unix:/run/authservice.sock"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1  # (2 × CPU) + 1
worker_class = "gthread"
threads = 2
worker_connections = 1000
max_requests = 1000  # Restart worker nach X requests (Memory Leak Prevention)
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/authservice/access.log"
errorlog = "/var/log/authservice/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "authservice"

# Server Mechanics
daemon = False
pidfile = "/run/authservice.pid"
user = "authservice"
group = "www-data"
umask = 0o007

# SSL (falls direkt über Gunicorn statt NGINX)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=auth_service.settings",
]

# Preload App (schnellere Worker-Starts)
preload_app = True

# Worker Lifecycle Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Starting Auth Service...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Reloading Auth Service...")

def when_ready(server):
    """Called just after the server is started."""
    print("Auth Service is ready. Spawning workers...")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    print("Forked child, re-executing.")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    print(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"Worker received SIGABRT signal (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"Worker exited (pid: {worker.pid})")
