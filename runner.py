"""
Runner is a wrapper for any command with some useful options.

Usage: runner.py [OPTIONS] '[CMD]'
"""

import click
import subprocess
import psutil
import time
import logging


class Command(object):
    """A command wrapper to run the command."""

    def __init__(
        self,
        cmd=[],
        attempts=1,
        sys_trace=False,
        call_trace=False,
        log_trace=False
    ):
        """
        Initiate the command wrapper.

        Parameters
        ----------
        cmd : list
            The command to run (default is empty).
        attempts : int
            Number of allowed failed attempts (default is 1).
        sys_trace : bool
            A flag indicating if system trace should be enabled (default is False).
        call_trace : bool
            A flag indicating if call trace should be enabled (default is False).
        log_trace : bool
            A flag indicating if log trace should be enabled (default is False).
        """
        if len(cmd) == 0:
            raise ValueError('No command specified')

        if call_trace:
            cmd = ['strace'] + cmd

        self.__cmd = cmd
        self.__attempts = attempts
        self.__call_trace = call_trace
        self.__sys_trace = sys_trace
        self.__log_trace = log_trace
        self.__return_codes = {}
        self.__captured_sys_trace = None

    def execute(self, repeat_times=1):
        """Executing a command and waiting for it to complete.

        Parameters
        ----------
        repeat_times : int
            Number of times to run command (default is 1).
        """
        logging.debug('execute()')

        for _ in range(repeat_times):
            # Stop execution when there are no more attempts.
            if self.attempts == 0:
                logging.debug('execute() -> attempts = 0')
                return

            logging.debug('execute() -> subprocess.Popen()')

            # Start execution of the command.
            process = subprocess.Popen(
                self.__cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            # If enabled, will capture the system trace.
            if self.__sys_trace:
                self.__captured_sys_trace = capture_sys_trace(process.pid)

            # Wait for the command to complete.
            stdout, stderr = process.communicate()
            process.wait()

            # Called only after the command has completed.
            self.__executed(process.returncode, stdout, stderr)

    def __executed(self, code, stdout, stderr):
        """Called when the command has finished executing.

        Parameters
        ----------
        code : bool
            The return code of the command.
        stdout : ellipsis
            Standard command output.
        stderr : ellipsis
            Standard command error.
        """
        logging.debug(f'__on_executed() -> return_code: {code}')

        # If the return code is not 0, then it failed.
        if code != 0:
            self.attempts -= 1

            if self.__sys_trace:
                create_log_file('sys-trace', self.__captured_sys_trace)

            if self.__call_trace:
                create_log_file('call-trace', f'\n{stderr.decode()}')

            # TODO: click.echo() should not be in the command class.
            if self.__log_trace:
                if stdout:
                    click.echo(f'\n{stdout.decode()}')

                if stderr:
                    click.echo(f'\n{stderr.decode()}')

        # Add or update the return code for the execution summary.
        self.__return_codes[code] = self.__return_codes.get(code, 0) + 1

    @property
    def attempts(self):
        """Returns the attempts."""
        logging.debug('attempts.getter')
        return self.__attempts

    @attempts.setter
    def attempts(self, value):
        """Set the attempts value.

        Parameters
        ----------
        value : int
            The new value.
        """
        logging.debug('attempts.setter')
        self.__attempts = value

    def summary(self):
        """Returns a summary of the command execution."""
        logging.debug('summary()')

        result = '--- command execution statistics ---'
        codes = self.__return_codes

        # If no return codes are available, return the result.
        if len(codes) == 0:
            logging.debug('summary() -> len(__return_codes) = 0')
            return result

        # Add all return codes to the result.
        for key, value in codes.items():
            result += (f'\nreturn code: {key} amount: {value}')

        # Add the most frequent return code to the result.
        result += f'\nmost frequent return code: {max(codes, key=codes.get)}'
        return result


def capture_sys_trace(process_id):
    """Captures and returns the system trace for the specified process.

    Parameters
    ----------
    process_id : int
        The process identifier.
    """
    logging.debug('capture_sys_trace()')

    # Captures the specified process.
    process = psutil.Process(process_id)

    # Receives a trace and returns it.
    return [f'Disk I/O: {str(psutil.disk_io_counters(perdisk=False))}',
            f'\n% Memory: {str(process.memory_percent())}',
            f'\n% CPU: {str(process.cpu_percent())}',
            f'\nThreads: {str(process.threads())}',
            f'\nNetwork Counters: {str(psutil.net_io_counters())}']


def create_log_file(name, content):
    """Create a log file.

    Parameters
    ----------
    name : str
        Name of the log file.
    content : str
        Log file content.
    """
    logging.debug('create_log_file()')

    # Set name for the log file.
    name = f'{name}-{time.strftime("%H-%M-%S", time.localtime())}.log'

    # Create a log file and write lines.
    file = open(name, 'w')
    file.writelines(content)
    file.close()


command = None


@click.command()
@click.option(
    '-c',
    '--count',
    default=1,
    metavar='COUNT',
    help='Number of times to run the given command.')
@click.option(
    '--failed-count',
    default=-1,
    metavar='N',
    help='Number of allowed failed command invocation attempts.')
@click.option(
    '--sys-trace',
    is_flag=True,
    help='If execution fails, a system trace log will be created.')
@click.option(
    '--call-trace',
    is_flag=True,
    help='If execution fails, a system calls log will be created.')
@click.option(
    '--log-trace',
    is_flag=True,
    help='If execution fails, add the command output logs.')
@click.option(
    '--debug',
    is_flag=True,
    help='Show each instruction executed by the script.')
@click.argument(
    'cmd',
    default='',
    metavar="'[CMD]'")
def run(
    count,
    failed_count,
    sys_trace,
    call_trace,
    log_trace,
    debug,
    cmd
):
    """Command wrapper to run any command."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    click.echo(f'Executing: {cmd}')

    # NOTE: Using a global variable is not good practice,
    # but it's only used to get information from it.
    global command

    # Creates a new command.
    command = Command(
        cmd=cmd.split(),
        attempts=failed_count,
        sys_trace=sys_trace,
        call_trace=call_trace,
        log_trace=log_trace)

    # Runs a command and waits for it to complete.
    command.execute(repeat_times=count)

    # When the command completes, print a summary of the execution.
    click.echo(command.summary())


def main():
    # If an interruption occurs, print the summary execution.
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        if command is not None:
            click.echo(command.summary())


if __name__ == '__main__':
    main()
