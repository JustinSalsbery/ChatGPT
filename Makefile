# author: Justin Salsbery

# File settings:
FILE := chat
INSTALL_DIR := /usr/local/bin

# Make settings:
.ONESHELL:
.SILENT:

SHELL := bash

.PHONY: help options
help options:
	echo "options:"
	echo -e "\tinstall"
	echo -e "\tuninstall"
	echo -e "\toptions (this)"

.PHONY: install
install:
	cp ${FILE}.py ${INSTALL_DIR}/${FILE}
	chmod +x ${INSTALL_DIR}/${FILE}

.PHONY: uninstall
uninstall:
	rm -f ${INSTALL_DIR}/${FILE}
