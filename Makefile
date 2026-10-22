PROJECT = letteredolive
OUTDIR = $(CURDIR)/dist/
# Build version: 0.0.0.dev<YYYYMMDDHHMMSS>, unique per build (shared script in the meta-repo).
# Override WHEELS_DIR when building outside the meta-repo.
WHEELS_DIR ?= $(CURDIR)/../dist-wheels
VERSION_SCRIPT ?= $(CURDIR)/../scripts/next_version.sh
VERSION ?= $(shell $(VERSION_SCRIPT) 0.0.0.dev $(WHEELS_DIR))
MEDIA = /run/media/jam/BEA6-BBCE/work/$(PROJECT)/
PYTHON = $(HOME)/.venv/bin/python

.PHONY: all clean build sdist version deploy

all:

clean:
	-rm *~
	$(MAKE) -C src clean

build: version
	cd src && $(PYTHON) ./setup.py build

sdist: version
	cd src && $(PYTHON) ./setup.py sdist

version:
	@echo '__version__ = "$(VERSION)"' > src/letteredolive/_version.py
	@echo 'githash = "'`git log -1 --format='%H' | cut -c 1-16`'"' >> src/letteredolive/_version.py
	@echo 'datestamp = "$(shell date +%Y%m%d%H%M)"' >> src/letteredolive/_version.py

push:
	git push

backup:
	rsync --recursive --verbose --exclude=.venv . $(MEDIA)

www:
	$(MAKE) -C www prod

test:
	cd src && $(PYTHON) -m pytest letteredolive/tests/ -v

deploy: build

.PHONY: test deploy
