@echo off
pushd "%~dp0"

set def_port=8000
set def_ip=127.0.0.1
set index=1

python-3.6.5.exe  InstallAllUsers=1 Include_pip=1 PrependPath=1 Include_test=1 Include_tools=1 Include_tcltk=1 Include_lib=1 Include_dev=1 Include_debug=1

timeout 3 > nul

set /P inputuser=Press any key to once the python installation complete: 

python -V 

if not %errorlevel% equ 0 (
   @echo:
   echo python needs to installed
   @echo:
   set /P input=Press any key to exit: 
   goto endlocal
)

pip install Django
pip install django-common-helpers
pip install django-cron
pip install django-tables2
pip install python-dateutil
pip install pytz
pip install quickfix
pip install requests
pip install setuptools
pip install simplejson
pip install six
pip install urllib3
pip install webcolors
pip install websocket-client
pip install wheel
pip install ws4py

goto endlocal

python manage.py makemigrations lic
python manage.py migrate

:while

echo IP address to use [default: %def_ip%][? for help]:
@echo:


set /P input=:
set ip=%input%

if "%input%" == "?" (
  echo Available IP address from this machine:
  @echo:
  ipconfig | findstr IPv4
  @echo:
  @echo:
  set input=
  goto while
)
if "%input%" == "" (
  set ip=%def_ip%
  @echo:
  goto portno
)

:portno

echo Port number [default: %def_port%]:
@echo:

set /P port=:
if "%port%" == "" (set port=%def_port%)

python manage.py runserver %ip%:%port% 
@echo:
@echo:

:endlocal
