@echo off
setlocal

pushd %~dp0

echo Creating virtualenv...
python -m venv env || goto end

call env\Scripts\activate.bat || goto end

echo.
echo Installing Python dependencies...
pip install -r requirements.txt || goto end

echo.
call manage.bat update

:end
popd
endlocal
pause
