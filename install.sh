#!/bin/sh
command -v python >/dev/null 2>&1 || { echo >&2 "Python is not present. Install it through your favourite package manager."; exit 1; }

echo "Installing Python packages"
pip install -r requirements.txt
pip install -e .
command -v npm >/dev/null 2>&1 || { echo >&2 "NPM is not present. Install node.js and try again."; exit 1; }
echo "Installing node.js packages"
npm install -g bower gulp
npm install
bower install
gulp