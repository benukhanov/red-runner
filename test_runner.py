from click.testing import CliRunner
from runner import run


def test_run_and_return_success():
    runner = CliRunner()
    result = runner.invoke(run, ['hostname'])
    assert result.exit_code == 0
