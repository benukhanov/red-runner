# Red Runner

Red Runner is a wrapper for any command with some useful options.

## Quickstart

Build:

`docker build . -t red-runner:latest`

Run:

`docker run red-runner:latest runner.py [OPTIONS] '[COMMAND]'`

Test:

`docker run red-runner:latest -m pytest`