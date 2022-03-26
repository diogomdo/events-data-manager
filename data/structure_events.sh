#!/bin/bash

if [ ! -d "./gDrive_backup" ] || [ -z "$(ls -A "./gDrive_backup")"  ]; then
  echo "No backed up events in /drive"
  exit 1
fi

for entry in "./gDrive_backup"/*
do
  filename=$(basename "$entry")
  fname="${filename%.*}"
  echo "$fname"

  month=$(echo "$fname" | cut -d- -f2)
  echo "$month"
  day=$(echo "$fname" | cut -d- -f3 | cut -d_ -f1)
  echo "$day"

  if [ ! -d "./events" ]; then
    # Control will enter here if $DIRECTORY doesn't exist.
    mkdir -p -- "./events"
  fi

  if [ ! -d "./events/"{"$month"}"/"{"$day"} ]; then
    # Control will enter here if $DIRECTORY doesn't exist.
    echo "Create folder"
    mkdir -p -- "./events/$month/$day"
  fi

  if [ ! -f "./events/${month}/${day}/${filename}" ]; then
     mv "$entry" "./events/${month}/${day}/${filename}"
  fi

  if [ -z "$(ls -A "./gDrive_backup")" ]; then
    rm -rf "./gDrive_backup"
  fi
done