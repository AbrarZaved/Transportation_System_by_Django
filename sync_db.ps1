#!/bin/bash

# MySQL Credentials
# MySQL Credentials
$DB_USER = "root"
$DB_NAME = "TRANSPORTATION"
$DUMP_FILE = "backups\backup.sql"

# Ask for action
if ($args[0] -eq "export") {
    Write-Host "Exporting database..."
    mysqldump -u $DB_USER -p $DB_NAME > $DUMP_FILE
    Write-Host "Database exported to $DUMP_FILE"
}
elseif ($args[0] -eq "import") {
    Write-Host "Importing database..."
    Get-Content $DUMP_FILE | mysql -u $DB_USER -p $DB_NAME
    Write-Host "Database imported from $DUMP_FILE"
}
else {
    Write-Host "Usage: .\sync_db.ps1 [export|import]"
}

