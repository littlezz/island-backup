bundle:
	pyinstaller -n island_backup cli.py -y
	cp -r island_backup/templates dist/island_backup/
	cd dist/; tar -zcvf island_backup.tar.gz island_backup/
