import pytest
from pgcmd import compose_exec, parse_dsn, pg_dump_cmd, pg_restore_cmd

URL = "postgresql+asyncpg://game:s%40cret@db:5433/game"


def test_parse():
    assert parse_dsn(URL) == {"user": "game", "password": "s@cret", "host": "db", "port": 5433, "db": "game"}
    assert parse_dsn("postgresql://u:p@localhost/x")["port"] == 5432
    for bad in ("mysql://u:p@h/x", "postgresql://u:p@h/"):
        with pytest.raises(ValueError):
            parse_dsn(bad)


def test_dump():
    argv, env = pg_dump_cmd(URL, "/backups/game.dump")
    assert argv == ["pg_dump", "-Fc", "--no-owner", "-h", "db", "-p", "5433", "-U", "game", "-d", "game",
                    "-f", "/backups/game.dump"]
    assert env == {"PGPASSWORD": "s@cret"}
    assert not any("cret" in a for a in argv)


def test_restore():
    argv, env = pg_restore_cmd(URL, "/backups/game.dump", jobs=4)
    assert argv[:6] == ["pg_restore", "--clean", "--if-exists", "--no-owner", "-j", "4"]
    assert argv[-3:] == ["-d", "game", "/backups/game.dump"] and env["PGPASSWORD"] == "s@cret"


def test_compose():
    argv, env = pg_dump_cmd(URL, "/tmp/x")
    c = compose_exec("db", argv, env)
    assert c[:4] == ["docker", "compose", "exec", "-T"]
    assert c[4:7] == ["-e", "PGPASSWORD=s@cret", "db"] and c[7:] == argv
