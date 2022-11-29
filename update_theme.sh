#!/bin/bash -e

if [ ! -d "360-ds" ]; then
  echo "Script must be run from the top level directory"
  exit 1
fi

git submodule update --init --remote 360-ds

cd 360-ds
npm update
npm run compile-sass -- --project 'grantnav' --path '../grantnav/frontend/static/css/'

echo "Theme compiled and updates ready to be committed"
