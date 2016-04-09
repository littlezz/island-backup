bundle:
	pyinstaller -n island_backup cli.py -y
	cp -r island_backup/templates dist/island_backup/
	tar -zcvf island_backup.tar.gz dist/island_backup
