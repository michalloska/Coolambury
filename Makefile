PYTHON = python3
SERVER_APP := $(shell pwd)/Server/server.py
CLIENT_APP := $(shell pwd)/Client/RunClient.py
CONFIG_PATH = $(shell pwd)/config.json
SET_PYTHONPATH := PYTHONPATH='.'

server: .FORCE
	$(SET_PYTHONPATH) $(PYTHON) $(SERVER_APP) $(CONFIG_PATH)

client: .FORCE
	$(SET_PYTHONPATH) $(PYTHON) $(CLIENT_APP) $(CONFIG_PATH)

clean: .FORCE
	find . -name '__pycache__' -exec rm -rf {} \;
.PHONY: .FORCE
FORCE:
