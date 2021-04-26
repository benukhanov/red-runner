# Red Runner

Red Runner is a wrapper for any command with some useful options.

## Quickstart

### Locally
> 💡 You need to install Python and open project folder.

Run:

`python3 runner.py [OPTIONS] '[CMD]'`

Test:

`python3 -m pytest`

### Docker
> 💡 You need to install Docker locally.

Build:

`docker build . -t red-runner:latest`

Run:

`docker run red-runner:latest runner.py [OPTIONS] '[CMD]'`

Test:

`docker run red-runner:latest -m pytest`