import click
import subprocess


class Command(object):
    def __init__(self, __tries):
        self.__tries = __tries
        self.__return_codes = {}

    def execute(self, cmd, count=1):
        for _ in range(count):
            process = subprocess.run(cmd)
            code = process.returncode

            self.update_tries(code)
            self.update_return_codes(code)

            if self.get_tries() == 0:
                return

    def update_tries(self, code):
        if code == 0:
            return

        self.__tries -= 1

    def get_tries(self):
        self.__tries

    def update_return_codes(self, code):
        codes = self.__return_codes

        if len(codes) > 0:
            codes[code] = codes[code] + 1
        else:
            codes[code] = 1

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
@ click.option('-c', '--count', default=1, metavar='COUNT', help='Number of times to run the given command.')
@ click.option('--failed-count', default=-1, metavar='N', help='Number of allowed failed command invocation attempts before giving up.')
@ click.argument('cmd', default='')
def run(count, failed_count, cmd):
    global command
    command = Command(failed_count)

    if validate_command(cmd):
        command.execute(cmd.split(), count)

    click.echo(command.get_summary())


def validate_command(cmd):
    return cmd != ''


def main():
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        if command is not None:
            click.echo(command.get_summary())


if __name__ == '__main__':
    main()
