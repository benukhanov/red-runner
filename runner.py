import click
import subprocess


class CommandWrapper(object):
    def __init__(self, __tries):
        self.__tries = __tries
        self.__return_codes = {}

    def execute(self, command):
        process = subprocess.run(command)
        code = process.returncode

        self.update_tries(code)
        self.update_return_codes(code)

    def update_tries(self, code):
        if code != 0:
            self.__tries -= 1

    def get_tries(self):
        self.__tries

    def update_return_codes(self, code):
        if len(self.__return_codes) > 0:
            self.__return_codes[code] = self.__return_codes[code] + 1
        else:
            self.__return_codes[code] = 1

    def print_summary(self):
        click.echo("\n--- command execution statistics ---")

        if len(self.__return_codes) > 0:
            for key, value in self.__return_codes.items():
                click.echo("return code: %s" % key + " amount: %s" % value)

            click.echo("most frequent return code: %s" %
                       max(self.__return_codes, key=self.__return_codes.get))


command_wrapper = None


@ click.command()
@ click.option('-c', '--count', default=1, metavar='COUNT', help='Number of times to run the given command.')
@ click.option('--failed-count', default=-1, metavar='N', help='Number of allowed failed command invocation attempts before giving up.')
@ click.argument('command', default='')
def run(count, failed_count, command):
    global command_wrapper
    command_wrapper = CommandWrapper(failed_count)

    if command != '':
        for _ in range(count):
            command_wrapper.execute(command.split())

            if command_wrapper.get_tries() == 0:
                break

    click.echo(command_wrapper.print_summary())


def main():
    try:
        run(standalone_mode=False)
    except click.exceptions.Abort:
        if command_wrapper is not None:
            click.echo(command_wrapper.print_summary())


if __name__ == '__main__':
    main()
