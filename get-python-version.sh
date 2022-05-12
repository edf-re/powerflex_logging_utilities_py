#!/bin/bash
set -x
grep python .tool-versions | cut -d' ' -f2
