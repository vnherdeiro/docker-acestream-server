# Docker Ace Stream server (tailored to MacOS X)
An [Ace Stream](http://www.acestream.org/) server Docker image.
- [Overview](#overview)
- [Building](#building)
- [Usage](#usage)
- [Reference](#reference)

## Overview
What this provides:
- Dockerized Ace Stream server (version `3.1.16`) running under Debian 8 (Jessie) slim.
- Bash script to start server and present HTTP API endpoint to host.
- Python playback script [`playstream.py`](playstream.py) instructing server to:
	- Commence streaming of a given program ID.
	- Start ([VLC](https://www.videolan.org/vlc/)) media player to view stream.

## Building
To build Docker image:
```sh
$ ./build.sh
```

## Usage
Start the server via:
```sh
$ ./run.sh
```

A program ID can be started with [`playstream.py`](playstream.py):
```sh
$ ./playstream.py --help
usage: playstream.py [-h] --ace-stream-pid HASH [--player PLAYER] [--progress]
                     [--server HOSTNAME] [--port PORT]

Instructs server to commence a given program ID. Will optionally execute a
local media player (VLC) once playback has started.

arguments:
  -h, --help            show this help message and exit
  --ace-stream-pid HASH
                        program ID to stream
```


All credits to [magnetikonline](https://github.com/magnetikonline).