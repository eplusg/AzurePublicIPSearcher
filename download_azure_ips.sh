#!/bin/bash

# Determine the script's directory
script_dir=$(dirname "$0")

# Get the download page content
page_content=$(curl -s 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519')

# Extract the download URL of the JSON file, ensuring only the URL is captured
download_url=$(echo "$page_content" | perl -nle 'print $1 if /href="(https:\/\/[^"]+\.json)"/' | head -n 1)

# Replace /data/aztools/ with a writable directory, e.g., ~/aztools/
backup_folder="${script_dir}/backup/"
max_archived_files=3

# Ensure the backup directory exists
mkdir -p "$backup_folder"

# Check if the old file exists and move it to the backup folder with the current date
if [ -e "azure_ips.json" ]; then
  current_date=$(date +"%Y%m%d") # Changed date format for clarity
  mv azure_ips.json "${backup_folder}azure_ips_backup_${current_date}.json"

  # Delete old backup files if there are more than max_archived_files
  num_archived_files=$(ls -1 ${backup_folder}azure_ips_backup_*.json | wc -l)
  if [ "$num_archived_files" -gt "$max_archived_files" ]; then
    files_to_delete=$((num_archived_files - max_archived_files))
    ls -t ${backup_folder}azure_ips_backup_*.json | tail -n $files_to_delete | xargs rm --
  fi
fi

# Use curl to download the JSON file if wget is not available
if command -v wget &> /dev/null; then
    wget -O azure_ips_new.json "$download_url"
else
    curl -o azure_ips_new.json "$download_url"
fi

# Replace the old file with the downloaded file
mv azure_ips_new.json azure_ips.json