# Installation Guide - Windows

## Current Status

- ❌ Python: Not properly installed (only Windows Store redirect found)
- ❌ Node.js: Not installed or not in PATH
- ✅ Winget: Available (v1.12.350)

## Step-by-Step Installation

### 1. Install Python 3.12

**Option A: Using winget (Recommended)**

```powershell
winget install Python.Python.3.12
```

**Option B: Manual Download**

1. Go to <https://www.python.org/downloads/>
2. Download Python 3.12.x (Windows installer 64-bit)
3. Run installer
4. ✅ **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"

### 2. Install Node.js 20 LTS

**Option A: Using winget (Recommended)**

```powershell
winget install OpenJS.NodeJS.LTS
```

**Option B: Manual Download**

1. Go to <https://nodejs.org/>
2. Download LTS version (20.x)
3. Run installer
4. Accept all defaults (will add to PATH automatically)

### 3. Restart Terminal

**CRITICAL**: After installation, you MUST restart your PowerShell terminal for PATH changes to take effect.

Close and reopen your terminal, then verify:

```powershell
python --version
node --version
npm --version
```

You should see:

- Python 3.12.x
- Node.js v20.x.x  
- npm 10.x.x

### 4. Install UV (Python Package Manager)

Once Python is working:

```powershell
python -m pip install uv
```

Or:

```powershell
pip install uv
```

---

## Quick Verification

Run these commands after restarting terminal:

```powershell
# Check Python
python --version

# Check pip
pip --version

# Check Node.js
node --version

# Check npm
npm --version
```

All should work without errors.

---

## Next Steps After Installation

1. ✅ Restart terminal
2. ✅ Verify installations
3. ✅ Install UV: `pip install uv`
4. ✅ Navigate to project: `cd c:\Users\muhds\.gemini\antigravity\scratch\AI-Dev-Tools-Zoomcamp-2025\Project\quantitative-finance-calculator`
5. ✅ Follow QUICKSTART.md

---

## Troubleshooting

### "Python not found" after installation

- Make sure you checked "Add Python to PATH" during installation
- Restart terminal
- If still not working, manually add to PATH:
  - Typical location: `C:\Users\<username>\AppData\Local\Programs\Python\Python312`

### "node not found" after installation

- Restart terminal (Node.js installer should add to PATH automatically)
- Typical location: `C:\Program Files\nodejs`

### WindowsApps python redirect

This is not a real Python installation. Disable it:

1. Settings → Apps → Advanced app settings → App execution aliases
2. Turn OFF both Python aliases

---

## Alternative: Use Online Development Environment

If local installation is problematic, consider:

1. **GitHub Codespaces** - Cloud VS Code with Python/Node pre-installed
2. **Replit** - Online Python/Node environment
3. **Google Colab** - For Python only (Jupyter notebooks)

Then deploy directly to Render without local testing.

---

**Current Project Location**:  
`c:\Users\muhds\.gemini\antigravity\scratch\AI-Dev-Tools-Zoomcamp-2025\Project\quantitative-finance-calculator\`

**Once installed**, continue with `QUICKSTART.md`
