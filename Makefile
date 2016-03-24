##
# This is a very simple Makefile for installing all of the dot-files to the
# current users's home directory.  Any files that already exist will be
# skipped.

SHELL=/bin/bash
# To avoid looping over unintended files or folders, build a filter list:
FILTERLIST=.git . .. *.swp $(wildcard .*.swp)
# Filter out anything in that filter list:
FILES=$(filter-out $(FILTERLIST),$(wildcard .*))
# Create target install file paths for matching make rules:
INSTALLED_FILES=$(addprefix ~/,$(FILES))

##
# copy_if_dne src dest 
# Copies the src file to dest if the dest doesn't already exist.
define copy_if_dne
   [ ! -e $(2) ] && (cp -r $(1) $(2); echo copied $(1) to home) || echo $(2) exists, not copied
endef

##
# Explain what's going to happen and then prompt to make sure they user really
# wants to blindly copy my dot-files to their home.
help:
	@echo This makefile will install all the following files, as long as they do not already exist.  If they already exist, they will be skipped.
	@echo $(INSTALLED_FILES)
	@read -p "continue? (y/N)" CONTINUE && [ $$CONTINUE = "y" ] && make install || echo aborting

install: $(INSTALLED_FILES)

##
# Target to match any relative file to a file in the user's home.
~/%: %
	@$(call copy_if_dne,$<,$@)
