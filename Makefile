

all:
	@echo "make sdist | install | bdist | twine"


clean:
	rm -f */*pyc
	rm -rf build dist qlmux.egg-info

.PHONY: sdist install bdist


bdist:
	python3 setup.py $@
sdist:
	python3 setup.py $@
install:
	python3 setup.py $@
twine:
	twine upload dist/*
