@echo off
cd /d "%~dp0outputs\mu\backend"
echo ============================================
echo   ?????? - AI ??????
echo ============================================
echo.
echo ?????? (?? 8000)...
echo ????? http://localhost:8000
echo ? Ctrl+C ????
echo.
.\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --host 0.0.0.0
pause
