bundle:
	pyinstaller -n island_backup cli.py -y
	cp -r island_backup/templates dist/island_backup/

