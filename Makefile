PYTHON=python2.7
BUILD_DIR=build

PACKAGES_DIR=$(BUILD_DIR)/site-packages
PACKAGES_DEV_DIR=test/site-packages-dev
STUB_DIR=test/stub

MKDIR=mkdir
RM=rm -rf
CP=cp -vr

.PHONY: build test

$(PACKAGES_DIR):
	$(PYTHON) -m pip install -r requirements.txt --target $(PACKAGES_DIR)

$(PACKAGES_DEV_DIR):
	# $(PYTHON) -m pip install -r requirements-dev.txt --target $(PACKAGES_DEV_DIR)

$(BUILD_DIR):
	$(CP) src/ $(BUILD_DIR)/

test: $(BUILD_DIR) $(PACKAGES_DEV_DIR) $(PACKAGES_DIR)
	$(RM) $(STUB_DIR) || true
	$(MKDIR) $(STUB_DIR) || true
	STUB_DIR=$(STUB_DIR) PACKAGES_DIR=$(PACKAGES_DIR) PACKAGES_DEV_DIR=$(PACKAGES_DEV_DIR) $(PYTHON) test/test_mg.py
	STUB_DIR=$(STUB_DIR) PACKAGES_DIR=$(PACKAGES_DIR) PACKAGES_DEV_DIR=$(PACKAGES_DEV_DIR) $(PYTHON) test/test_trigger_parsing.py

clean:
	$(RM) $(BUILD_DIR) || true
	$(RM) $(STUB_DIR) || true
	$(RM) $(PACKAGES_DEV_DIR) || true

