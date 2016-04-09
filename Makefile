version = $(shell python -c "print(__import__('island_backup').version)")
name = island_backup-$(version).win-amd64

default:bundle

version:
	@echo $(version)
	@echo $(name)

bundle:
	pyinstaller -n island_backup cli.py -y
	cp -r island_backup/templates dist/island_backup/
	cd dist/; tar -zcvf $(name).tar.gz island_backup/
