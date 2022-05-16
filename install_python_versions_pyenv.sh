#!/bin/sh

PythonVersionsArray=( "3.8:latest" "3.9:latest" "3.10:latest" "3.11:latest"
"pypy3.9:latest" )

PythonVersionsString="${PythonVersionsArray[@]}"
 
for version in $PythonVersionsString; do
  pyenv install $version
done

pyenv local $PythonVersionsString

echo
echo "Make sure there are * next to Python versions $PythonVersionsString"
echo 

pyenv versions
