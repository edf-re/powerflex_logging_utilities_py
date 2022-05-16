#!/bin/bash

asdf plugin-add python

PythonVersionsArray=( "3.8" "3.9" "3.10" "3.11" "pypy" )
PythonVersionsString="${PythonVersionsArray[@]}"
LatestPythonVersionsArray=()

for version in $PythonVersionsString; do
  latestVersion=$(asdf list all python $version | tail -1)
  LatestPythonVersionsArray+=($latestVersion)
  set -x
  asdf install python $latestVersion
  set +x
done

LatestPythonVersionsString="${LatestPythonVersionsArray[@]}"
asdf local python $LatestPythonVersionsString
