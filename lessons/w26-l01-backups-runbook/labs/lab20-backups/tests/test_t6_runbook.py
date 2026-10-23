from runbook import check_runbook

GOOD = """# Runbook: восстановление базы
## Когда применять
База потеряна или испорчена.
## Перед началом
Объявить в чате команды, остановить API: `docker compose stop api`.
## Шаги
1. Найти свежий бэкап: `ls -t /backups | head -1`
2. Проверить sha256: `python -m backup verify FILE`
3. Восстановить: `PGPASSWORD=$PGPASSWORD pg_restore --clean -d game FILE`
4. Запустить API: `docker compose start api`
## Проверка
`curl -f https://staging…/health` и число строк как в манифесте.
## Откат
Если не взлетело — вернуть предыдущий бэкап по тем же шагам.
## Контакты
Капитан команды, преподаватель.
"""


def test_good():
    assert check_runbook(GOOD) == []


def test_missing_sections():
    text = GOOD.replace("## Откат", "## Что-то").replace("## Контакты\n", "")
    assert check_runbook(text) == ["нет раздела: Откат", "нет раздела: Контакты"]


def test_few_steps_and_no_command():
    text = GOOD.replace("2. Проверить sha256: `python -m backup verify FILE`\n", "")
    text = text.replace("4. Запустить API: `docker compose start api`", "3. Запустить API")
    assert check_runbook(text) == ["шаг 3 без команды"]
    text2 = GOOD.split("1. ")[0] + "1. Всё восстановить `make restore`\n## Проверка\nок\n## Откат\n-\n## Контакты\n-\n"
    assert check_runbook(text2) == ["мало шагов: 1"]


def test_secrets():
    bad = GOOD.replace("PGPASSWORD=$PGPASSWORD", "PGPASSWORD=hunter2")
    assert check_runbook(bad) == ["секрет в строке 9"]
    ok = GOOD + "Токен бота: token = <в менеджере паролей>\npassword: ${DB_PASSWORD}\n"
    assert check_runbook(ok) == []
    assert check_runbook(GOOD + "secret: abc\n") == ["секрет в строке 17"]
