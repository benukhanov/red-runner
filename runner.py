import click
import subprocess


@click.command()
@click.option('-c', default=1, metavar='COUNT', help='Number of times to run the given command.')
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def run(c, command):
    for _ in range(c):
        subprocess.run(command)


if __name__ == '__main__':
    run()
