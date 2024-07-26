install:
	pip install -r requirements.txt
	cd src/monitor/frontend && npm install && cd ../../..

test-all: 
	PYTHONPATH=src/:${PYTHONPATH} pytest test

test-sender:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/sender/

test-generator:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/generator/

test-backend:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/monitor/

test-queue:
	PYTHONPATH=src/:${PYTHONPATH} pytest test/msg_queue/