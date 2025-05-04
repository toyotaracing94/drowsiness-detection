# Automate Installation
- sudo sh setup.sh

# Manual Installation Ngrok in Raspberrypi
## Init
- download
	- wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
- unzip to used global user
	- sudo tar xvzf ./ngrok-v3-stable-linux-arm64.tgz -C /usr/local/bin
- setup
	- ngrok authtoken NGROK_AUTHTOKEN
		- replace NGROK_AUTHTOKEN with your unique ngrok authtoken found in the ngrok dashboard.


## Setup ssh global access & test it
- ngrok tcp 22
	- now the port is running with given information in raspberrypi
- test ssh connection from local machine using different network
	- ssh -p NGROK_PORT USER@NGROK_TCP_ADDRESS
		- NGROK_PORT: The port number of the ngrok agent (i.e. if the agent shows tcp://1.tcp.ngrok.io:12345, your port number is 12345.
		- USER: A valid ssh login to access your remote device's operating system.
		- NGROK_TCP_ADDRESS: The address of the ngrok agent (i.e. if the agent shows tcp://1.tcp.ngrok.io:12345, your TCP address is 1.tcp.ngrok.io.

## Adding Auth Token Config
```bash
ngrok authtoken USED_YOUR_TOKEN_FROM_DASHBOARD_HERE
```

## Editing Config
```bash
ngrok config edit
```