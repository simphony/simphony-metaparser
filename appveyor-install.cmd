"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

pip install -r requirements.txt

rem install simphony-common 
python setup.py develop
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..
