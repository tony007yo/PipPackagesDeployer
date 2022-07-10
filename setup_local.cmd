@echo off

set MODULE_NAME=UMCommonUtils
set BUILD_NUMBER=1.0.0

if not "%1"=="" (
  set BUILD_NUMBER=1.0.%1.dev0
)

set CUR_DIR=%~dp0
set PYTHON_VERSION=3.7
set PYTHON_VENV=env

py -%PYTHON_VERSION% -m venv --clear %PYTHON_VENV%
echo Prepare environment for Python %PYTHON_VERSION%
call env\Scripts\activate
python -m pip install --upgrade pip setuptools wheel twine || goto :error
python -m pip install -r requirements.txt --no-cache-dir || goto :error

echo %BUILD_NUMBER%>version.txt
echo. & echo Building %MODULE_NAME% %BUILD_NUMBER% package... & echo.
python setup.py sdist bdist_wheel || goto :error
deactivate
echo. & echo Building %MODULE_NAME% %BUILD_NUMBER% package done
exit /b 0

:error
deactivate
echo. & echo Failed to build %MODULE_NAME% %BUILD_NUMBER% package!
exit /b %errorlevel%