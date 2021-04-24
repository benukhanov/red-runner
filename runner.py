import click
import subprocess


class CommandWrapper(object):
    def __init__(self, __failed_count):
        self.__failed_count = __failed_count

    def execute(self, command):
        process = subprocess.run(command)
        code = process.returncode

        self.update_failed_count(code)

    def update_failed_count(self, code):
        if code != 0:
            self.__failed_count -= 1

    def get_failed_count(self):
        self.__failed_count


@ click.command()
@ click.option('-c', default=1, metavar='COUNT', help='Number of times to run the given command.')
@ click.option('--failed-count', default=-1, metavar='N', help='Number of allowed failed command invocation attempts before giving up.')
@ click.argument('command', default='')
def run(c, failed_count, command):
    global command_wrapper
    command_wrapper = CommandWrapper(failed_count)

    if command != '':
        for _ in range(c):
            command_wrapper.execute(command.split())

            if command_wrapper.get_failed_count() == 0:
                break


command_wrapper = None

if __name__ == '__main__':
    run(standalone_mode=False)
