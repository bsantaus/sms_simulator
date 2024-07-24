# SMS Simulation

The repository provides a configurable SMS simulator (like for an emergency alert service).

The simulator here is comprised of three components: a Message Generator, Message Senders, and a Progress Monitor.
The Generator creates random messages to send to random phone numbers, the Senders consume the messages and attempt to send them after a random length of time, and the Progress Monitor displays simple statistics concerning how many messages have been sent, how many have failed, and the average time per a message.

## Installation

This project is built on both Python (Generator, Senders, Monitor backend) and Svelte (Monitor frontend).

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

