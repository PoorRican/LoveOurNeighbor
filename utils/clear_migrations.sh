#!/bin/bash

# this script removes all django database migration tables
# these are particularly pesky during development

# go to the root of the directory
pwd=$(pwd)
if [[ "$pwd" =~ "utils" ]]; then
  cd ..
fi

# iterate all directories, deleting migration folder, and then recreating
ROOT=$(ls)
for d in $ROOT; do
  if [[ -d $d ]]; then
    DIR="$d"/migrations
    if [[ -e $DIR ]]; then
      echo deleting "$DIR"
      rm -rf "$DIR"
      mkdir "$DIR"
      chmod 777 "$DIR"
      touch "$DIR"/__init__.py
      chmod 777 "$DIR"/__init__.py
    fi
  fi
done