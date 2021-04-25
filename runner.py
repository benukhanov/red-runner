import click
import subprocess
import psutil
import time


class Command(object):
    def __init__(self, tries=1):
        self.__tries = tries
        self.__return_codes = {}

    def execute(self, cmd, repeat_times=1, sys_trace=False):
        if len(cmd) == 0:
            return

        for _ in range(repeat_times):
            if self.tries == 0:
                return

            process = subprocess.Popen(cmd)

            if sys_trace:
                save_sys_trace(capture_sys_trace(process.pid))

            process.wait()

            code = process.returncode

            if code != 0:
                self.tries -= 1

            self.__return_codes[code] = self.__return_codes.get(code, 0) + 1

    @property
    def tries(self):
        return self.__tries

    @tries.setter
    def tries(self, value):
        self.__tries = value

    def summary(self):
        result = '\n--- command execution statistics ---'
        codes = self.__return_codes

        if len(codes) == 0:
            return result

        for key, value in codes.items():
            result += ("\nreturn code: %s" % key + " amount: %s" % value)

        result += "\nmost frequent return code: %s" % max(codes, key=codes.get)
        return result


def capture_sys_trace(process_id):
    process = psutil.Process(process_id)

    return ["Disk I/O: {}".format(str(psutil.disk_io_counters(perdisk=False))),
            "\n% Memory: {}".format(str(process.memory_percent())),
            "\n% CPU: {}".format(str(process.cpu_percent())),
            "\nThreads: {}".format(str(process.threads())),
            "\nNetwork Counters: {}".format(str(psutil.net_io_counters()))]


def save_sys_trace(log):
    current_time = time.strftime("%H-%M-%S", time.localtime())
    file = open("sys-trace-{}.log".format(current_time), "w")
    file.writelines(log)
    file.close()


command = None


@ click.command()
@ click.option(
    '-c',
    '--count',
    default=1,
    metavar='COUNT',
    help='Number of times to run the given command.')
@ click.option(
    '--failed-count',
    default=-1,
    metavar='N',
    help='Number of allowed failed command invocation attempts.')
@ click.option(
    '--sys-trace',
    is_flag=True,
    help='If execution fails, a system trace log will be created.'
)
@ click.argument(
    'cmd',
    default='')
def run(count, failed_count, sys_trace, cmd):
    global command
    command = Command(tries=failed_count)
    command.execute(cmd=cmd.split(), repeat_times=count, sys_trace=sys_trace)

    click.echo(command.summary())


def main():
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        if command is not None:
            click.echo(command.summary())


if __name__ == '__main__':
    main()
