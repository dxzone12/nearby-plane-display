#!/bin/bash

echo "Updating tar1090 aircraft database..."
wget -O /usr/local/share/tar1090/aircraft.csv.gz https://github.com/wiedehopf/tar1090-db/raw/csv/aircraft.csv.gz
echo "Done."

echo "Updating SDM aircraft database..."

# Create temp file for the zip
echo "Creating tmp file and output directory..."
TMP_ZIP=$(mktemp /tmp/standing-data-XXXXXX.zip)
mkdir -p /usr/local/share/npd/standing-data

echo "Downloading standing-data repo to temp file: $TMP_ZIP"
wget -O "$TMP_ZIP" https://github.com/vradarserver/standing-data/archive/refs/heads/main.zip

echo "Extracting to /usr/local/share/npd/standing-data"
unzip -o "$TMP_ZIP" -d /usr/local/share/npd

echo "Cleaning up tmp file"
# Optionally clean up
rm "$TMP_ZIP"

echo "SDM aircraft database update complete."
