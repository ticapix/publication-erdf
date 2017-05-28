PYTHON=python2.7
BUILD_DIR=build

PACKAGES_DIR=$(BUILD_DIR)/site-packages
STUB_DIR=test/stub

MKDIR=mkdir
RM=rm -rf

.phony: test

$(PACKAGES_DIR):
	$(PYTHON) -m pip install -r requirements.txt --target $(PACKAGES_DIR)

install: $(PACKAGES_DIR)

test: install
	# $(RM) $(STUB_DIR) || true
	# $(MKDIR) $(STUB_DIR) || true
	# STUB_DIR=$(STUB_DIR) PACKAGES_DIR=$(PACKAGES_DIR) $(PYTHON) test/test_mg.py
	STUB_DIR=$(STUB_DIR) PACKAGES_DIR=$(PACKAGES_DIR) $(PYTHON) test/test_parsing_message.py

clean:
	$(RM) $(PACKAGES_DIR) || true
	$(RM) $(STUB_DIR) || true
