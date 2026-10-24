PROJECT = letteredolive
OUTDIR = $(CURDIR)/dist/
# Build version: 0.0.2.dev<YYYYMMDDHHMMSS>, unique per build (shared script in the meta-repo).
# Override WHEELS_DIR when building outside the meta-repo.
WHEELS_DIR ?= $(CURDIR)/../dist-wheels
VERSION_SCRIPT ?= $(CURDIR)/../scripts/next_version.sh
VERSION ?= $(shell $(VERSION_SCRIPT) 0.0.2.dev $(WHEELS_DIR))
MEDIA = /run/media/jam/BEA6-BBCE/work/$(PROJECT)/
PYTHON = $(HOME)/.venv/bin/python
# Install prefix for `prod` (the global launchers and their venv). Set with `deploy letteredolive.prod --prefix`.
PREFIX ?= $(or $(DEPLOY_PREFIX),/var/lib/zoid6/venv)
SYSPY ?= /usr/bin/python3
BIN_DIR ?= /usr/local/bin

.PHONY: all clean build sdist version deploy venv prod

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

# venv: build, then install into the user's venv ($(HOME)/.venv). `deploy` is kept as an alias.
venv: build
	$(PYTHON) -m pip install --no-index --find-links $(WHEELS_DIR) letteredolive

deploy: venv

# prod: root only. Builds a fresh wheel with the system Python (not $(HOME)/.venv, since sudo sets HOME to
# /root), installs it into $(PREFIX), and writes the three launchers (letteredolive, shell, bbs) into
# $(BIN_DIR), each running $(PREFIX)/bin/python. Never creates the venv; never --break-system-packages.
prod:
	@if [ "$$(id -u)" -ne 0 ]; then echo "prod: run as root (sudo make prod)"; exit 1; fi
	@if [ ! -x "$(PREFIX)/bin/python" ]; then echo "prod: $(PREFIX)/bin/python is missing. Create it as root first: $(SYSPY) -m venv $(PREFIX)"; exit 1; fi
	@echo '__version__ = "$(VERSION)"' > src/letteredolive/_version.py
	cd src && $(SYSPY) ./setup.py -q bdist_wheel --dist-dir $(WHEELS_DIR)
	$(PREFIX)/bin/python -m pip install --no-index --find-links $(WHEELS_DIR) letteredolive
	@for name in letteredolive shell bbs; do \
		printf '#!/bin/sh\n# %s: the BBS shell (package "shell"). Installed by make prod; runs %s.\nexec -a "$$0" %s/bin/python -W all -m shell "$$@"\n' "$$name" "$(PREFIX)" "$(PREFIX)" > "$(BIN_DIR)/$$name"; \
		chmod 755 "$(BIN_DIR)/$$name"; \
	done
	@echo "prod: installed into $(PREFIX); launchers in $(BIN_DIR)"

.PHONY: test
