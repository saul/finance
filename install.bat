@echo off
setlocal

echo Creating virtualenv...
python -m venv env || goto end

call %~dp0\env\Scripts\activate.bat || goto end

echo Installing Python dependencies...
pip install -r requirements.txt || goto end

echo Updating...
call manage.bat update

:end
endlocal
pause
