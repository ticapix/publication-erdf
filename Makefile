PYTHON=python2.7
BUILD_DIR=build

.phony: test

$(BUILD_DIR)/site-packages:
	$(PYTHON) -m pip install -r requirements.txt --target $(BUILD_DIR)/site-packages

install: $(BUILD_DIR)/site-packages

test: install
	$(PYTHON) test/test_mg.py
#	MESSAGE=test/dump-81e2fccb-f1db-41df-8ca3-41350d5e0750-body.dat python2 parse-email/run.py
	# REQ=trigger-parsing/test/body.dat MG_API_KEY=key-fcb58f6eeab931d2d75291d29f6068e2 python2 trigger_email/run.py
