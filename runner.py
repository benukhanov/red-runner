"""
A wrapper for any command with some useful options.

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
        tries=1,
        sys_trace=False,
        call_trace=False,
        log_trace=False
    ):
        if len(cmd) == 0:
            raise ValueError('No command specified')

        if call_trace:
            cmd = ['strace'] + cmd

        self.__cmd = cmd
        self.__tries = tries
        self.__call_trace = call_trace
        self.__sys_trace = sys_trace
        self.__log_trace = log_trace
        self.__return_codes = {}
        self.__captured_sys_trace = None

    def execute(self, repeat_times=1):
        """Executing a command and waiting for it to complete."""
        logging.debug('execute()')

        for _ in range(repeat_times):
            # Stop execution when there are no more tries.
            if self.tries == 0:
                logging.debug('execute() -> tries = 0')
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
        """Called when the command has finished executing."""
        logging.debug(f'__on_executed() -> return_code: {code}')

        # If the return code is not 0, then it failed.
        if code != 0:
            self.tries -= 1

            # If system tracing is enabled, create a log file.
            if self.__sys_trace:
                create_log_file('sys-trace', self.__captured_sys_trace)

            # If call tracing is enabled, create a log file.
            if self.__call_trace:
                create_log_file('call-trace', f'\n{stderr.decode()}')

            # If log tracing is enabled, add the command output logs (stdout).
            if stdout and self.__log_trace:
                # TODO: click.echo() should not be in the command class.
                click.echo(f'\n{stdout.decode()}')

            # If log tracing is enabled, add the command output logs (stderr).
            if stderr and self.__log_trace:
                # TODO: click.echo() should not be in the command class.
                click.echo(f'\n{stderr.decode()}')

        # Add or update the return code for the execution summary.
        self.__return_codes[code] = self.__return_codes.get(code, 0) + 1

    @property
    def tries(self):
        """Returns the tries."""
        logging.debug('tries.getter')
        return self.__tries

    @tries.setter
    def tries(self, value):
        """Set the tries value."""
        logging.debug('tries.setter')
        self.__tries = value

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
    """Captures and returns the system trace for the specified process."""
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
    """Create a log file."""
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
    """A wrapper for any command with some useful options."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    click.echo(f'Executing: {cmd}')

    # NOTE: Using a global variable is not good practice,
    # but it's only used to get information from it.
    global command

    # Creates a new command.
    command = Command(
        cmd=cmd.split(),
        tries=failed_count,
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
