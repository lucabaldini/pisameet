all:


clean:
	rm -rf pisameet/__pycache__
	cd docs; make clean

html:
	cd docs; make html