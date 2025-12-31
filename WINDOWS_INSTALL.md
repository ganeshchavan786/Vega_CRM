# 🖥️ VEGA CRM - Windows 10/11 Installation Guide

## Customer साठी Production Ready Setup (Docker शिवाय)

---

## 📋 System Requirements

| Requirement | Minimum |
|-------------|---------|
| OS | Windows 10 / Windows 11 |
| RAM | 4 GB |
| Disk Space | 2 GB |
| Internet | Initial setup साठी |

---

## 🚀 Quick Installation (3 Steps)

### Step 1: Python Install करा
1. Download: https://www.python.org/downloads/
2. Installer run करा
3. **IMPORTANT:** ✅ "Add Python to PATH" checkbox check करा!
4. "Install Now" click करा

### Step 2: VEGA CRM Install करा
1. `windows` folder उघडा
2. `install.bat` वर Right-click करा
3. "Run as administrator" select करा
4. Installation complete होईपर्यंत wait करा (5-10 min)

### Step 3: CRM Start करा
- Desktop वर "VEGA CRM" shortcut double-click करा
- Browser automatically उघडेल: http://localhost:8000

---

## 📁 Installation Files

```
windows/
├── install.bat           # Main installer (पहिले run करा)
├── start.bat             # Server start करा
├── stop.bat              # Server stop करा
├── install-service.bat   # Windows Service (auto-start)
├── uninstall.bat         # CRM remove करा
└── README.txt            # Help guide
```

---

## ⚙️ Auto-Start Setup (Optional)

Windows boot झाल्यावर CRM automatically start व्हायला हवे असेल तर:

1. `install-service.bat` वर Right-click करा
2. "Run as administrator" select करा
3. Done! CRM आता Windows सोबत start होईल

---

## 📦 Customer Package बनवा

Customer ला देण्यासाठी ZIP package बनवायचे असेल:

```batch
windows\create-package.bat
```

हे `dist\VegaCRM-Windows-Setup.zip` file बनवेल जे customer ला देता येईल.

---

## 🔧 Commands

| Action | Command |
|--------|---------|
| Start Server | `C:\VegaCRM\start.bat` |
| Stop Server | `C:\VegaCRM\stop.bat` |
| Start Service | `net start VegaCRM` |
| Stop Service | `net stop VegaCRM` |
| Check Status | `sc query VegaCRM` |

---

## 📂 Important Paths

| Item | Path |
|------|------|
| Installation | `C:\VegaCRM\` |
| Database | `C:\VegaCRM\data\` |
| Logs | `C:\VegaCRM\logs\` |
| Config | `C:\VegaCRM\app\config\` |

---

## 🔄 Backup & Restore

### Backup:
```batch
xcopy /E /I C:\VegaCRM\data D:\Backup\VegaCRM-Data
```

### Restore:
```batch
xcopy /E /I D:\Backup\VegaCRM-Data C:\VegaCRM\data
```

---

## ❓ Troubleshooting

### "Python not found" error?
- Python install करा
- "Add to PATH" checkbox check करा

### Port 8000 already in use?
- `C:\VegaCRM\run_production.py` मध्ये port बदला

### Server start होत नाही?
- `C:\VegaCRM\logs\` folder check करा

### Data backup कसा करायचा?
- `C:\VegaCRM\data\` folder copy करा

---

## 📞 Support

- GitHub: https://github.com/ganeshchavan786/Vega_CRM
- Issues: https://github.com/ganeshchavan786/Vega_CRM/issues
