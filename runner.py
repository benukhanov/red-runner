import click
import subprocess
import psutil
import time
import logging


class Command(object):
    def __init__(
            self,
            cmd=[],
            tries=1,
            sys_trace=False,
            call_trace=False,
            log_trace=False):
        if len(cmd) == 0:
            raise ValueError("No command specified")

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
        logging.debug('execute()')

        for _ in range(repeat_times):
            if self.tries == 0:
                logging.debug('execute() -> tries = 0')
                return

            logging.debug('execute() -> subprocess.Popen()')

            process = subprocess.Popen(
                self.__cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            if self.__sys_trace:
                self.__captured_sys_trace = capture_sys_trace(process.pid)

            stdout, stderr = process.communicate()
            process.wait()

            self.__executed(process.returncode, stdout, stderr)

    def __executed(self, code, stdout, stderr):
        logging.debug(f'__on_executed() -> return_code: {code}')

        if code != 0:
            self.tries -= 1

            if self.__sys_trace:
                create_log('sys-trace', self.__captured_sys_trace)

            if self.__call_trace:
                create_log('call-trace', f'\n{stderr.decode()}')

            if stdout and self.__log_trace:
                click.echo(f'\n{stdout.decode()}')

            if stderr and self.__log_trace:
                click.echo(f'\n{stderr.decode()}')

        self.__return_codes[code] = self.__return_codes.get(code, 0) + 1

    @property
    def tries(self):
        logging.debug('tries.getter')
        return self.__tries

    @tries.setter
    def tries(self, value):
        logging.debug('tries.setter')
        self.__tries = value

    def summary(self):
        logging.debug('summary()')

        result = '--- command execution statistics ---'
        codes = self.__return_codes

        if len(codes) == 0:
            logging.debug('summary() -> len(__return_codes) = 0')
            return result

        for key, value in codes.items():
            result += ("\nreturn code: %s" % key + " amount: %s" % value)

        result += "\nmost frequent return code: %s" % max(codes, key=codes.get)
        return result


def capture_sys_trace(process_id):
    logging.debug('capture_sys_trace()')

    process = psutil.Process(process_id)

    return ["Disk I/O: {}".format(str(psutil.disk_io_counters(perdisk=False))),
            "\n% Memory: {}".format(str(process.memory_percent())),
            "\n% CPU: {}".format(str(process.cpu_percent())),
            "\nThreads: {}".format(str(process.threads())),
            "\nNetwork Counters: {}".format(str(psutil.net_io_counters()))]


def create_log(name, content):
    logging.debug('create_log()')

    name = f'{name}-{time.strftime("%H-%M-%S", time.localtime())}.log'
    file = open(name, "w")
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
    default='')
def run(count, failed_count, sys_trace, call_trace, log_trace, debug, cmd):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    click.echo("Executing: %s" % cmd)

    global command
    command = Command(
        cmd=cmd.split(),
        tries=failed_count,
        sys_trace=sys_trace,
        call_trace=call_trace,
        log_trace=log_trace)
    command.execute(repeat_times=count)

    click.echo(command.summary())


def main():
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        if command is not None:
            click.echo(command.summary())


if __name__ == '__main__':
    main()
