.PHONY: setup test run smoke

PYTHON ?= .venv/bin/python

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install --requirement requirements.txt

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

run:
	PYTHONPATH=src $(PYTHON) -m coinbase_adapter.main --output output/market_trades.jsonl

smoke:
	PYTHONPATH=src $(PYTHON) -m coinbase_adapter.main --output output/smoke-market-trades.jsonl --max-market-messages 2
