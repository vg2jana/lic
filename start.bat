@echo off
pushd "%~dp0"

set def_port=8000
set def_ip=127.0.0.1
set index=1

python-3.6.5.exe  InstallAllUsers=1 Include_pip=1 PrependPath=1 Include_test=1 Include_tools=1 Include_tcltk=1 Include_lib=1 Include_dev=1 Include_debug=1

timeout 3 > nul

set /P inputuser=Press any key once the python installation complete: 

python -V 

if not %errorlevel% equ 0 (
   @echo:
   echo python needs to installed
   @echo:
   set /P input=Press any key to exit: 
   goto endlocal
)

pip install Django==2.1
pip install django-common-helpers==0.9.1
pip install django-cron==0.5.0
pip install django-tables2==1.21.2
pip install python-dateutil==2.7.3
pip install pytz==2018.4
pip install requests==2.19.1
pip install setuptools==39.0.1
pip install simplejson==3.16.0
pip install six==1.11.0
pip install urllib3==1.23
pip install webcolors==1.8.1
pip install websocket-client==0.46.0
pip install wheel==0.33.1
pip install ws4py==0.5.1


python manage.py makemigrations insurance
python manage.py migrate
python manage.py createsuperuser

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
