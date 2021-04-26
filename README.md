# Red Runner

Red Runner is a wrapper for any command with some useful options.

## Command Line Options

```bash
╰─$ python3 runner.py --help
Usage: runner.py [OPTIONS] '[CMD]'

  Command wrapper to run any command.

Options:
  -c, --count COUNT  Number of times to run the given command.
  --failed-count N   Number of allowed failed command invocation attempts.
  --sys-trace        If execution fails, a system trace log will be created.
  --call-trace       If execution fails, a system calls log will be created.
  --log-trace        If execution fails, add the command output logs.
  --debug            Show each instruction executed by the script.
  --help             Show this message and exit.
```

## Example

```bash
╰─$ python3 runner.py --log-trace 'ping'
Executing: ping

ping: usage error: Destination address required

--- command execution statistics ---
return code: 1 amount: 1
most frequent return code: 1
```

## Python Dependencies

- [pytest](https://pypi.org/project/pytest/)
- [click](https://pypi.org/project/click/)
- [psutil](https://pypi.org/project/psutil/)

## Quickstart

### Locally
> 💡 You need to install Python and open project folder.

Install:

`pip3 install -r requirements.txt`

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

## Challenges

Challenges encountered while working on the Red Runner.

- Understanding how to make solution simple and with minimal dependencies.
- PyPI packages and what to choose to use.
- Make the solution not complex and focus on simplicity and readability of the code.
- Make code testable as possible.
- Make each feature independent from the other features.

# Resources

Links to resources that were used to learn while working on the Red Runner.

- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Subprocess Docs](https://docs.python.org/3/library/subprocess.html)
- [Subprocess.py Source Code](https://github.com/python/cpython/blob/master/Lib/subprocess.py#L460)
- [Using Alpine can make Python Docker builds 50× slower](https://pythonspeed.com/articles/alpine-docker-python/)
- [Single Python File Example](https://softwareengineering.stackexchange.com/a/243045)
- [Click Docs](https://click.palletsprojects.com/)
- [Why Click?](https://click.palletsprojects.com/why/)
- [pytest: How to mock in Python](https://changhsinlee.com/pytest-mock/)
- [Modern Test-Driven Development in Python](https://testdriven.io/blog/modern-tdd/)
- [Python Property Decorator](https://www.askpython.com/python/built-in-methods/python-property-decorator)
- [Tracing Python with strace or truss](https://rhodesmill.org/brandon/slides/2014-07-pyohio/strace/)
- [Documenting Python Code](https://realpython.com/documenting-python-code/)

# License

[MIT](https://choosealicense.com/licenses/mit/)