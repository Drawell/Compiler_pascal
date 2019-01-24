@echo off

if "%1"=="" (
  echo Usage %~nx0 ^<filename^>
  exit
)

rem set JAVA_HOME=C:\Program Files\Java\jdk1.7.0_11
rem set JAVA_HOME=C:\Program Files\Java\jdk1.8.0_144
set JAVA_HOME=C:\Program Files\Java\jdk1.8.0_144


set JAVAC="%JAVA_HOME%\bin\javac.exe"
set JAVAP="%JAVA_HOME%\bin\javap.exe"
set JASPER="%JAVA_HOME%\bin\java.exe" -jar "%~dp0\jasper\jasper.jar"
set JASMIN="%JAVA_HOME%\bin\java.exe" -jar "%~dp0\jasmin-2.4\jasmin.jar"
set PYTHON="C:\Users\HP\AppData\Local\Programs\Python\Python36\python.exe"



%PYTHON% "%~dp0main.py" %1

set FILENAME=%~nx1

rem %JAVAC% -target 1.5 -source 1.5 %FILENAME%.java
rem %JASPER% %FILENAME%.class
%JASMIN% %1.j
::Java %FILENAME%