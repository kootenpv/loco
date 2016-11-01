""" Our tests are defined in here """
from loco.loco import ls
from loco.loco import remove_user
from click.testing import CliRunner

cli = CliRunner()


def test_ls():
    cli.invoke(ls)


def test_remove_user():
    cli.invoke(remove_user, ["loco0"])
