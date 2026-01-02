"""
VEGA CRM - Build Windows EXE
Creates standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("    VEGA CRM - Building Windows EXE")
    print("=" * 50)
    print()
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Install PyInstaller if not present
    print("[1/5] Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
    
    # Create spec file content
    print("[2/5] Creating build configuration...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
project_root = r"{project_root}"

a = Analysis(
    [os.path.join(project_root, 'windows', 'vega_crm_app.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'app'), 'app'),
        (os.path.join(project_root, 'frontend'), 'frontend'),
        (os.path.join(project_root, 'guides'), 'guides'),
    ],
    hiddenimports=[
        # Uvicorn
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        # FastAPI & Starlette
        'fastapi',
        'fastapi.applications',
        'fastapi.routing',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'fastapi.middleware.gzip',
        'fastapi.middleware.httpsredirect',
        'fastapi.middleware.trustedhost',
        'fastapi.staticfiles',
        'fastapi.templating',
        'fastapi.responses',
        'fastapi.requests',
        'fastapi.security',
        'fastapi.encoders',
        'starlette',
        'starlette.applications',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.middleware.base',
        'starlette.middleware.errors',
        'starlette.middleware.authentication',
        'starlette.staticfiles',
        'starlette.templating',
        'starlette.responses',
        'starlette.requests',
        'starlette.websockets',
        'starlette.background',
        'starlette.concurrency',
        'starlette.config',
        'starlette.datastructures',
        'starlette.exceptions',
        'starlette.formparsers',
        'starlette.status',
        # Pydantic
        'pydantic',
        'pydantic.fields',
        'pydantic.main',
        'pydantic.types',
        'pydantic.validators',
        'pydantic_settings',
        # SQLAlchemy - all modules
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.orm.session',
        'sqlalchemy.orm.query',
        'sqlalchemy.orm.mapper',
        'sqlalchemy.orm.relationships',
        'sqlalchemy.orm.properties',
        'sqlalchemy.orm.strategy_options',
        'sqlalchemy.ext',
        'sqlalchemy.ext.asyncio',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.ext.declarative.api',
        'sqlalchemy.ext.hybrid',
        'sqlalchemy.engine',
        'sqlalchemy.pool',
        'sqlalchemy.sql',
        'sqlalchemy.sql.expression',
        'sqlalchemy.sql.functions',
        'sqlalchemy.sql.sqltypes',
        'sqlalchemy.dialects',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.aiosqlite',
        'sqlalchemy.event',
        'sqlalchemy.exc',
        'sqlalchemy.schema',
        'sqlalchemy.types',
        'sqlalchemy.util',
        'aiosqlite',
        'greenlet',
        # Other dependencies
        'httptools',
        'websockets',
        'watchfiles',
        'python_multipart',
        'multipart',
        'email_validator',
        'passlib',
        'passlib.hash',
        'passlib.handlers',
        'passlib.handlers.bcrypt',
        'jose',
        'python_jose',
        'bcrypt',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        'sniffio',
        'h11',
        'click',
        'typing_extensions',
        'annotated_types',
        # App modules - all routes, controllers, models, etc.
        'app',
        'app.main',
        'app.config',
        'app.database',
        'app.config.email_config',
        # Routes
        'app.routes',
        'app.routes.auth',
        'app.routes.company',
        'app.routes.user',
        'app.routes.customer',
        'app.routes.contact',
        'app.routes.lead',
        'app.routes.deal',
        'app.routes.task',
        'app.routes.activity',
        'app.routes.email_sequence',
        'app.routes.permission',
        'app.routes.audit',
        'app.routes.logs',
        'app.routes.admin',
        'app.routes.reports',
        'app.routes.data_management',
        'app.routes.nurturing',
        'app.routes.qualification',
        # Controllers
        'app.controllers',
        'app.controllers.auth_controller',
        'app.controllers.company_controller',
        'app.controllers.user_controller',
        'app.controllers.customer_controller',
        'app.controllers.contact_controller',
        'app.controllers.lead_controller',
        'app.controllers.deal_controller',
        'app.controllers.task_controller',
        'app.controllers.activity_controller',
        'app.controllers.permission_controller',
        # Models
        'app.models',
        'app.models.user',
        'app.models.company',
        'app.models.customer',
        'app.models.contact',
        'app.models.lead',
        'app.models.deal',
        'app.models.task',
        'app.models.activity',
        'app.models.email_sequence',
        'app.models.permission',
        'app.models.audit_trail',
        'app.models.log',
        'app.models.report',
        'app.models.password_reset',
        'app.models.user_company',
        # Middleware
        'app.middleware',
        'app.middleware.rate_limit',
        # Schemas
        'app.schemas',
        # Services
        'app.services',
        # Utils
        'app.utils',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VegaCRM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    spec_file = os.path.join(script_dir, 'VegaCRM.spec')
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print("[3/5] Building EXE (this may take 5-10 minutes)...")
    
    # Run PyInstaller
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        spec_file
    ], cwd=project_root)
    
    if result.returncode != 0:
        print("ERROR: Build failed!")
        return 1
    
    print("[4/5] Copying additional files...")
    
    dist_dir = os.path.join(project_root, 'dist')
    
    # Copy data folder template
    data_dir = os.path.join(dist_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create start script for EXE
    start_bat = os.path.join(dist_dir, 'Start VegaCRM.bat')
    with open(start_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('title VEGA CRM\n')
        f.write('echo Starting VEGA CRM...\n')
        f.write('echo Access at: http://localhost:8000\n')
        f.write('start http://localhost:8000\n')
        f.write('VegaCRM.exe\n')
        f.write('pause\n')
    
    print("[5/5] Creating README...")
    
    readme = os.path.join(dist_dir, 'README.txt')
    with open(readme, 'w') as f:
        f.write("VEGA CRM - Windows Application\\n")
        f.write("=" * 40 + "\\n\\n")
        f.write("To start VEGA CRM:\\n")
        f.write("1. Double-click 'Start VegaCRM.bat'\\n")
        f.write("2. Browser will open automatically\\n")
        f.write("3. Access: http://localhost:8000\\n\\n")
        f.write("To stop: Close the command window\\n")
    
    print()
    print("=" * 50)
    print("    BUILD COMPLETE!")
    print("=" * 50)
    print()
    print(f"EXE Location: {os.path.join(dist_dir, 'VegaCRM.exe')}")
    print()
    print("Files in dist folder:")
    print("  - VegaCRM.exe (main application)")
    print("  - Start VegaCRM.bat (easy launcher)")
    print("  - data/ (database folder)")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
