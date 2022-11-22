init:
	pip install -r requirements.txt
ratios:
	python3 ratios.py

.PHONY: init ratios
