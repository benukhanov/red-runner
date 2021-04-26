import pytest

from click.testing import CliRunner
from runner import run, Command


def test_should_fail_to_run_cmd_multiple_time():
    command = Command(cmd="ping", tries=3)
    command.execute(repeat_times=3)
    assert command.tries == 0


def test_should_run_cmd_multiple_times_and_succeed():
    command = Command(cmd="hostname", tries=3)
    command.execute(repeat_times=3)
    assert command.tries == 3


def test_should_set_tries_and_get_tries():
    command = Command("hostname", tries=1)
    command.tries = 0
    assert command.tries == 0


def test_should_raise_exception_when_no_command_specified():
    with pytest.raises(ValueError) as exception:
        command = Command(tries=1)

    assert "No command specified" in str(exception.value)


def test_should_get_summary_after_command_execution():
    command = Command(cmd="hostname", tries=3)
    command.execute()
    expected = ("--- command execution statistics ---"
                "\nreturn code: 0 amount: 1"
                "\nmost frequent return code: 0")
    result = command.summary()
    assert result == expected


def test_run_cmd_and_return_success():
    runner = CliRunner()
    result = runner.invoke(run, ['hostname'])
    assert result.exit_code == 0
