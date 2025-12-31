============================================
    VEGA CRM - Windows Installation Guide
    Production Ready for Windows 10/11
============================================

SYSTEM REQUIREMENTS:
- Windows 10 or Windows 11
- 4 GB RAM (minimum)
- 2 GB free disk space
- Internet connection (for initial setup)

============================================
INSTALLATION STEPS:
============================================

Step 1: Install Python
----------------------
1. Download Python 3.11 from: https://www.python.org/downloads/
2. Run the installer
3. IMPORTANT: Check "Add Python to PATH" checkbox!
4. Click "Install Now"

Step 2: Install VEGA CRM
------------------------
1. Right-click on "install.bat"
2. Select "Run as administrator"
3. Wait for installation to complete (5-10 minutes)

Step 3: Start VEGA CRM
----------------------
- Double-click "VEGA CRM" shortcut on Desktop
  OR
- Run C:\VegaCRM\start.bat

Step 4: Access CRM
------------------
Open browser and go to: http://localhost:8000

============================================
OPTIONAL: AUTO-START ON WINDOWS BOOT
============================================

If you want VEGA CRM to start automatically when Windows starts:
1. Right-click on "install-service.bat"
2. Select "Run as administrator"
3. Service will be installed and started

============================================
FILES INCLUDED:
============================================

install.bat         - Main installer (run first)
start.bat           - Start VEGA CRM server
stop.bat            - Stop VEGA CRM server
install-service.bat - Install as Windows Service (auto-start)
uninstall.bat       - Remove VEGA CRM completely

============================================
TROUBLESHOOTING:
============================================

Q: "Python not found" error?
A: Install Python and make sure "Add to PATH" is checked.

Q: Port 8000 already in use?
A: Change port in C:\VegaCRM\run_production.py

Q: Server won't start?
A: Check C:\VegaCRM\logs folder for error messages.

Q: How to backup data?
A: Copy C:\VegaCRM\data folder to safe location.

============================================
SUPPORT:
============================================

GitHub: https://github.com/ganeshchavan786/Vega_CRM
Email: support@vegacrm.com

============================================
