# shepherds-toolkit-apit

- poetry run python manage.py populate_bible --source=api --bible-version=NVI
- poetry run python manage.py populate_bible --source=api --bible-version=NVI --clear
-  Get-ChildItem -Recurse -Include *.py -Path . | Where-Object { $_.DirectoryName -match "migrations" -and $_.Name -ne "__init__.py" } | Remove-Item                    
- Get-ChildItem -Recurse -Include *.pyc -Path . | Remove-Item    
- python manage.py showmigrations