@echo off
echo 正在启动二次供水系统（绿色版）...
start cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul
start cmd /k "cd frontend-dist && python -m http.server 5173"
timeout /t 3 /nobreak >nul
echo 系统启动完成！
echo 前端访问地址：http://localhost:5173
echo 后端API地址：http://localhost:8000
start http://localhost:5173
pause
