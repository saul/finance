@echo off
setlocal
call %~dp0env\Scripts\activate.bat
set DJANGO_SETTINGS_MODULE=finance.settings
python manage.py %*
endlocal
