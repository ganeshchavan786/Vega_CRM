"""
Production Server Runner
Run with multiple workers using Gunicorn + Uvicorn
"""

import os
import sys
import multiprocessing

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings


def get_workers():
    """Calculate optimal number of workers based on CPU cores"""
    cores = multiprocessing.cpu_count()
    # Recommended: 2-4 workers per CPU core
    return min(settings.WORKERS, cores * 2 + 1)


def run_development():
    """Run development server with auto-reload"""
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )


def run_production():
    """Run production server with Gunicorn + Uvicorn workers"""
    try:
        import gunicorn.app.base
        
        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        workers = get_workers()
        options = {
            "bind": "0.0.0.0:8000",
            "workers": workers,
            "worker_class": settings.WORKER_CLASS,
            "timeout": settings.WORKER_TIMEOUT,
            "keepalive": settings.KEEP_ALIVE,
            "accesslog": "-",
            "errorlog": "-",
            "loglevel": settings.LOG_LEVEL.lower(),
        }
        
        print(f"Starting production server with {workers} workers...")
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Debug: {settings.DEBUG}")
        
        from app.main import app
        StandaloneApplication(app, options).run()
        
    except ImportError:
        print("Gunicorn not installed. Running with Uvicorn only...")
        print("Install gunicorn for production: pip install gunicorn")
        run_uvicorn_production()


def run_uvicorn_production():
    """Run production server with Uvicorn only (Windows compatible)"""
    import uvicorn
    
    workers = get_workers()
    print(f"Starting Uvicorn server with {workers} workers...")
    print(f"Environment: {settings.ENVIRONMENT}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=workers,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CRM SAAS Server Runner")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "uvicorn"],
        default="dev",
        help="Server mode: dev (development), prod (gunicorn), uvicorn (uvicorn workers)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of workers (overrides config)"
    )
    
    args = parser.parse_args()
    
    if args.workers:
        settings.WORKERS = args.workers
    
    print(f"=" * 50)
    print(f"  CRM SAAS Server - {settings.APP_VERSION}")
    print(f"=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")
    print(f"CORS Origins: {settings.ALLOWED_ORIGINS}")
    print(f"Background Tasks: {'Enabled' if settings.BACKGROUND_TASK_ENABLED else 'Disabled'}")
    print(f"=" * 50)
    
    if args.mode == "dev":
        run_development()
    elif args.mode == "prod":
        run_production()
    else:
        run_uvicorn_production()
