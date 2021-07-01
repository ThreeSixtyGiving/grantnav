#!/bin/zsh

set -e

build_styles ()
{
  cd 360-ds
  rm -rf node_modules
  npm i
  npx gulp build
  cd ..
  cp 360-ds/build/css/global.css grantnav/frontend/static/css/theme.css
}

version="$(node --version)"
echo $version
if [[ "$version" == "v12"* && -d "360-ds" ]]; 
then
  echo 'Node v12 running and 360-ds submodule exists'
  build_styles
else
  echo 'Please install node v12 and/or the 360-ds submodule.'
fi

