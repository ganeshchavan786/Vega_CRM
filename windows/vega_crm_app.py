"""
VEGA CRM - Windows Standalone Application
Entry point for PyInstaller EXE build
"""

import os
import sys
import webbrowser
import time
import logging
from threading import Timer

# Fix for windowed app - redirect stdout/stderr to devnull if not available
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# Set up paths for PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
    DATA_DIR = os.path.join(APP_DIR, 'data')
    LOG_DIR = os.path.join(APP_DIR, 'logs')
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    APP_DIR = BASE_DIR
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Add app to path
sys.path.insert(0, BASE_DIR)

# Create directories if not exists
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Set environment variables
os.environ['DATABASE_URL'] = f'sqlite:///{os.path.join(DATA_DIR, "crm.db")}'
os.environ['ENVIRONMENT'] = 'production'

# Setup file logging
log_file = os.path.join(LOG_DIR, 'vegacrm.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
    ]
)
logger = logging.getLogger('VegaCRM')


def open_browser():
    """Open browser after server starts"""
    time.sleep(3)
    webbrowser.open('http://localhost:8101')


def main():
    logger.info("=" * 50)
    logger.info("VEGA CRM - Windows Application Starting")
    logger.info("=" * 50)
    logger.info(f"Base Directory: {BASE_DIR}")
    logger.info(f"Data Directory: {DATA_DIR}")
    logger.info(f"Log Directory: {LOG_DIR}")
    logger.info("Starting server on http://localhost:8101")
    
    # Open browser in background
    Timer(3, open_browser).start()
    
    # Import and run uvicorn with file logging config
    import uvicorn
    
    # Custom logging config for windowed app
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "default",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["file"], "level": "INFO"},
            "uvicorn.error": {"handlers": ["file"], "level": "INFO"},
            "uvicorn.access": {"handlers": ["file"], "level": "INFO"},
        },
    }
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8101,
        log_config=log_config,
    )


if __name__ == "__main__":
    main()
