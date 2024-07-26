install:
	pip install -r requirements.txt
	cd src/monitor/frontend && npm install && cd ../../..

test: test-sender test-generator test-backend

test-sender:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/sender/

test-generator:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/generator/

test-backend:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/monitor/