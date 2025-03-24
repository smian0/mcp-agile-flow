#!/bin/bash
# Cleanup script for removing archived files after FastMCP migration

# Set -e to exit on error
set -e

# Create a backup of all archived files
echo "Creating backup of archived files..."
mkdir -p backups
timestamp=$(date +"%Y%m%d-%H%M%S")
backup_file="backups/archive-backup-${timestamp}.zip"

# Create zip backup of archive directories
zip -r "${backup_file}" tests/archive scripts/archive/legacy

# Check if backup was successful
if [ $? -eq 0 ] && [ -f "${backup_file}" ]; then
    echo "Backup created successfully at ${backup_file}"
    
    # Remove the archive directories
    echo "Removing archived files..."
    rm -rf tests/archive
    rm -rf scripts/archive
    
    echo "Cleanup completed successfully!"
    echo "If you need to restore the archived files, unzip ${backup_file}"
else
    echo "Error: Backup failed. Aborting cleanup."
    exit 1
fi 