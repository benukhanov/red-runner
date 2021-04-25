from click.testing import CliRunner
from runner import run, Command


def test_should_fail_to_run_cmd_multiple_time():
    command = Command(tries=3)
    command.execute(cmd="ping", repeat_times=3)
    assert command.tries == 0


def test_should_run_cmd_multiple_times_and_succeed():
    command = Command(tries=3)
    command.execute(cmd="hostname", repeat_times=3)
    assert command.tries == 3


def test_should_set_tries_and_get_tries():
    command = Command(tries=1)
    command.tries = 0
    assert command.tries == 0


def test_should_get_summary_after_command_execution():
    command = Command(tries=3)
    command.execute(cmd="hostname")
    expected = "\n--- command execution statistics ---\nreturn code: 0 amount: 1\nmost frequent return code: 0"
    result = command.summary()
    assert result == expected


def test_run_cmd_and_return_success():
    runner = CliRunner()
    result = runner.invoke(run, ['hostname'])
    assert result.exit_code == 0
