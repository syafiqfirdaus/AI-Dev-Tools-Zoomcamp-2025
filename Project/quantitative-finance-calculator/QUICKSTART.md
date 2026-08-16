# Quick Start Guide - Quantitative Finance Calculator

## Prerequisites Installation

Your system currently doesn't have Python, Node.js, or Docker installed. Here's how to install them:

### Option 1: Using Windows Package Manager (winget)

```powershell
# Install Python 3.12
winget install Python.Python.3.12

# Install Node.js LTS
winget install OpenJS.NodeJS.LTS

# Install Docker Desktop (optional, for containerized testing)
winget install Docker.DockerDesktop
```

### Option 2: Manual Download

1. **Python 3.12+**: Download from [python.org](https://www.python.org/downloads/)
2. **Node.js 20+**: Download from [nodejs.org](https://nodejs.org/)
3. **Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)

After installing, **restart your terminal** for changes to take effect.

---

## Quick Start (After Installation)

### 1. Install UV (Python Package Manager)

```powershell
pip install uv
```

### 2. Setup Backend

```powershell
cd c:\Users\muhds\.gemini\antigravity\scratch\AI-Dev-Tools-Zoomcamp-2025\Project\quantitative-finance-calculator\server

# Install dependencies
uv sync

# Run tests
uv run pytest --cov=app tests/ -v

# Start backend
uv run uvicorn app.main:app --reload
```

Backend will run at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

### 3. Setup Frontend

```powershell
cd c:\Users\muhds\.gemini\antigravity\scratch\AI-Dev-Tools-Zoomcamp-2025\Project\quantitative-finance-calculator\client

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend will run at: `http://localhost:5173`

---

## Docker Alternative

If you prefer using Docker:

```powershell
cd c:\Users\muhds\.gemini\antigravity\scratch\AI-Dev-Tools-Zoomcamp-2025\Project\quantitative-finance-calculator

docker-compose up --build
```

Access:

- Frontend: `http://localhost`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## What to Test

1. **Backend API**:
   - Visit `http://localhost:8000/docs`
   - Test compound interest endpoint
   - Check calculation accuracy

2. **Frontend UI**:
   - Open `http://localhost:5173`
   - Enter sample values in calculator
   - Verify chart visualization
   - Check calculation results

3. **Database**:
   - Make several calculations
   - Check history is saved
   - Verify pagination works

---

## Expected Test Results

### Backend Tests (27 tests)

```
test_calculations.py::TestCompoundInterest ✓✓✓✓✓
test_calculations.py::TestLoanAmortization ✓✓✓✓
test_calculations.py::TestInvestmentReturn ✓✓✓✓
test_calculations.py::TestRiskMetrics ✓✓✓✓
test_integration.py::TestCompoundInterestAPI ✓✓
test_integration.py::TestLoanAmortizationAPI ✓
test_integration.py::TestInvestmentReturnAPI ✓
test_integration.py::TestRiskMetricsAPI ✓
test_integration.py::TestHistoryAPI ✓✓✓✓
test_integration.py::TestHealthEndpoints ✓✓

Coverage: 95%+
```

---

## Troubleshooting

### "UV not found"

```powershell
pip install uv
# Or
python -m pip install uv
```

### "npm not found"

Restart terminal after Node.js installation

### Port already in use

```powershell
# Change port in server
uvicorn app.main:app --port 8001

# Or kill existing process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### CORS errors

Make sure both servers are running and `.env` file is configured

---

## Next Steps After Local Testing

1. ✅ Verify all tests pass
2. ✅ Test frontend functionality
3. ✅ Deploy to Render/Railway
4. ✅ Share on social media
5. ✅ Submit for peer review

---

**Project Location**:  
`c:\Users\muhds\.gemini\antigravity\scratch\AI-Dev-Tools-Zoomcamp-2025\Project\quantitative-finance-calculator\`

**Full Documentation**: See `README.md` and `walkthrough.md`
