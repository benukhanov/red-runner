import click
import subprocess


@click.command()
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def run(command):
    subprocess.run(command)


if __name__ == '__main__':
    run()
