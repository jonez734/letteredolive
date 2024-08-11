all:

clean:
	-rm *~
	$(MAKE) -C letteredolive clean

push:
	git push

version:
	@echo '__version__ = "'`git log -1 --format='%H' | cut -c 1-16`'"' > letteredolive/_version.py
	@echo '__datestamp__ = "'`date +%Y%m%d-%H%M`-`whoami`'"' >> letteredolive/_version.py

install: version build
	sudo ./setup.py install

build: version
	./setup.py build

sdist: version
	./setup.py sdist
