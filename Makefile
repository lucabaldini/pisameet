all:


clean:
	rm -rf pisameet/__pycache__
	rm -rf pm2024/__pycache__
	cd docs; make clean

html:
	cd docs; make html
