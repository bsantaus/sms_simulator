# SMS Simulation

The repository provides a configurable SMS simulator (like for an emergency alert service).

The simulator here is comprised of three components: a Message Generator, Message Senders, and a Progress Monitor.
The Generator creates random messages to send to random phone numbers, the Senders consume the messages and attempt to send them after a random length of time, and the Progress Monitor displays simple statistics concerning how many messages have been sent, how many have failed, and the average time per a message.

## Installation

This project is built on both Python (Generator, Senders, Monitor backend) and [Svelte](https://kit.svelte.dev/) (Monitor frontend).
The backend piece of the Monitor is implemented using [FastAPI](https://fastapi.tiangolo.com/).

Note that this project requires Python >= 3.10 as it makes use of the `match/case` construct introduced in that version.

If you have both Python (& pip) and Node.js version 20 installed, you can run `make install` to install all necessary dependencies and then skip the remainder of this section.

Alternatively, you can install all of the necessary Python dependencies using:

```bash
pip install -r requirements.txt
```

To install the necessary Node.js packages for the Svelte frontend, I recommend first installing Node.js version 20 through [NVM](https://github.com/nvm-sh/nvm), then installing the Node packages using `npm`:

```bash
nvm install 20 && nvm use 20
cd src/monitor/frontend 
npm install
```

## Running the Simulator

The simulator is run via one Python script located at [src/simulator.py](src/simulator.py). 

**Before running the simulator** you must build the frontend for the Progress Monitor. You can do this using `make build-frontend`.

The simulator can be called on its own to run the default configuration of the simulator, or with a number of command line arguments that can change its operation.

The default configuration of the simulator is as follows:

```
    Number of messages: 1000,
    Number of senders:  10,
    Each sender is initialized with:
        Mean delay:   0.5s
        Failure rate: 50%
    Monitor update interval: 1s
```

Generally, running the simulator can be done `python src/simulator.py <OPTIONS>`. 

You can get detailed information on the options available using `python src/simulator.py -h`.

There are two primary ways to change the simulator configuration: command-line arguments or a config file.
An example config file is located in [`src/config.json`](src/config.json).
Each field in the config file has a corresponding command-line flag with which the same value can be set.
Omission of any field in the config file is acceptable and the default value will be used, instead.

It is possible to use both a config file and command-line arguments for quick changes to a standard config. 
Note that any command-line arguments passed _before_ the config file argument will be ignored, and any flags used after the config file flag will override the config values.

## Viewing the Progress Monitor

The Progress Monitor component has two sub-components: a frontend application written in Svelte with Tailwind for styling and a backend API written using FastAPI.

The frontend application for the Monitor is served at [http://localhost:3000/](http://localhost:3000/) while the simulator is running.
If you would like to see it on its own, you can run `npm run dev` from the [src/monitor/frontend](src/monitor/frontend/) directory.

Should you want to see the backend API methods, you can do so at [http://localhost:8000/docs](http://localhost:8000/docs) while the application is running.
You can also run the backend on its own with `uvicorn main:app --port 8000` from the [src/monitor/backend](src/monitor/backend/) directory.

## Testing

Each component written in Python has an associated unit test suite. 

Test suites are visible in the [test/](test/) directory and are written using `pytest` and `unittest`.
API tests for the Progress Monitor also make use of the `TestClient` object provided by `FastAPI`.

You can run the tests for individual components using `make test-<component>` (view [Makefile](Makefile) for commands) or every suite using `make test-all`.


