import click
import subprocess


class Command(object):
    def __init__(self, tries=1):
        self.__tries = tries
        self.__return_codes = {}

    def execute(self, cmd, repeat_times=1):
        if len(cmd) == 0:
            return

        for _ in range(repeat_times):
            if self.tries == 0:
                return

            process = subprocess.run(cmd)
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

    def get_summary(self):
        result = '\n--- command execution statistics ---'
        codes = self.__return_codes

        if len(codes) == 0:
            return result

        for key, value in codes.items():
            result += ("\nreturn code: %s" % key + " amount: %s" % value)

        result += "\nmost frequent return code: %s" % max(codes, key=codes.get)
        return result


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
@ click.argument(
    'cmd',
    default='')
def run(count, failed_count, cmd):
    global command
    command = Command(tries=failed_count)
    command.execute(cmd=cmd.split(), repeat_times=count)

    click.echo(command.get_summary())


def main():
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        if command is not None:
            click.echo(command.get_summary())


if __name__ == '__main__':
    main()
