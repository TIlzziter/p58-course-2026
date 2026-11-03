# Практика: Консоль и Git руками (урок 02, пт 06.11)

> Рабочая версия 1 (29.10.2026): план перерабатывается по итогам встреч менторов, часть решений на согласовании и может измениться.

Восемь коротких заданий, на каждое 5–10 минут. Команды набираешь **сам, руками**. Агента можно спросить,
что делает команда или откуда взялась ошибка, но команды и скрипты из его ответа не копируем (это этап 0,
до конца декабря). В конце запускаешь самопроверку `check_console.py` и показываешь её вывод ментору.

## Где работаем

Подойдёт любой из трёх вариантов:

* **учебный сервер курса** (Linux): логин и адрес даёт преподаватель. Как войти с Windows и сделать SSH-ключ —
  в [инструкции](../../../../docs/server-windows.md), это же шаг 0 [лабораторной 01](../../labs/lab01-git-flow/README.md);
* **свой ноутбук**: терминал macOS или Linux; на Windows — WSL (Ubuntu) или Git Bash;
* **запасной вариант**, если на ноутбуке ничего не заводится, — GitHub Codespaces: открой репозиторий курса на GitHub →
  **Code → Codespaces → Create codespace**. Это Linux прямо в браузере, ставить ничего не надо, нужен только аккаунт GitHub.

Понадобятся `git` и Python 3.12+ (`python3 --version`). Если команда `python` не находится, пиши `python3`.

## Подготовка: рабочая папка и клон курса

```bash
mkdir -p ~/p58-console && cd ~/p58-console
git clone https://github.com/school58-project/p58-course-labs.git
```

Клон понадобится уже в задании 3, а остальной Git будет в задании 6.

## Что должно получиться в итоге

```
p58-console/                рабочая папка (имя любое)
├── project/
│   ├── frontend/
│   ├── backend/
│   ├── logic/
│   └── docs/
│       └── notes/
├── sandbox/
│   ├── notes.txt           задание 2
│   └── todo.txt            задание 3
├── hello.sh                задание 4
├── env.txt                 задание 5
├── p58-course-labs/        клон курса, своя ветка и about-<ник>.md (задание 6)
└── .venv/                  задание 7
```

## Задания

**1. Навигация.** `pwd`, `ls -la`, `cd`, `mkdir -p`. Собери дерево `project/` и `sandbox/` как на картинке выше,
одной-двумя командами `mkdir -p`. Проверь себя: `ls -la project` и `ls project/docs`.

**2. Файлы.** В `sandbox/`: `touch draft.txt` → `cp draft.txt copy.txt` → `mv copy.txt notes.txt` → `rm draft.txt`.
Потом полистай README лабораторной 01 через `cat`, `less` (выйти — `q`), `head -n 5` и `tail -n 5`.
В итоге в `sandbox/` лежит `notes.txt`, а `draft.txt` и `copy.txt` нет.

**3. Потоки.** Найди все TODO в файлах лабораторной 01, запиши их в файл, а в конец допиши, сколько их:

```bash
LAB=p58-course-labs/lessons/w01-l02-team-setup/labs/lab01-git-flow
grep -rn TODO "$LAB" > sandbox/todo.txt
grep -rn TODO "$LAB" | wc -l >> sandbox/todo.txt
```

Разберись, чем `>` отличается от `>>` и что делает `|` (подсказка: один из них молча затирает файл).
Допиши в `sandbox/notes.txt` одну строку через `echo ... >>`.

**4. Права и скрипты.** Создай в рабочей папке `hello.sh`: первая строка `#!/usr/bin/env bash`, дальше `echo`,
который печатает приветствие и первый аргумент `$1`. Сделай файл исполняемым (`chmod +x hello.sh`)
и запусти: `./hello.sh <ник>`. Сравни права до и после `chmod` через `ls -la`.

**5. Окружение.** Собери `env.txt`:

```bash
which python > env.txt              # или which python3
python --version >> env.txt         # или python3 --version
export P58_NICK=<ник>
echo "P58_NICK=$P58_NICK" >> env.txt
history | tail -n 5 >> env.txt
```

> ⚠️ Дальше два задания с Git и Python-окружением. Тут важна каждая буква, так что не торопись.

**6. Git.** Внутри `p58-course-labs/`:

```bash
git config --global user.name "<ник>"
git config --global user.email "<почта от GitHub>"
git log --oneline | head
git switch -c about/<ник>
```

Создай `about-<ник>.md` (3–5 строк: ник, какую роль в проекте хочешь, чему хочешь научиться) и закоммить его
в свою ветку (`git add`, `git commit -m "docs: about <ник>"`). **Только ник, без настоящего имени и фамилии.**
Пушить в репозиторий курса не нужно (и нельзя).

**7. Python-окружение.** В рабочей папке:

```bash
python -m venv .venv
source .venv/bin/activate           # Windows (Git Bash): source .venv/Scripts/activate
python -m pip install -r p58-course-labs/requirements.txt
cd p58-course-labs/lessons/w01-l02-team-setup/labs/lab01-git-flow
python check.py                     # таблица задач лабы: пока почти все НЕТ — это нормально
```

**8. Бонус дома.** `ssh-keygen -t ed25519`, потом публичный ключ (`cat ~/.ssh/id_ed25519.pub`) добавить в GitHub:
**Settings → SSH and GPG keys**. Приватный ключ (`id_ed25519` без `.pub`) никому не показываем, вообще никому.
Если работаешь на учебном сервере, это шаг 0 лабораторной 01, по шагам:
[ключ на своём компьютере](../../../../docs/server-windows.md#2-создать-ssh-ключ-на-своём-компьютере) и
[ключ сервера в GitHub](../../../../docs/server-windows.md#5-подключить-github-на-сервере).

## Самопроверка и сдача

```bash
python p58-course-labs/lessons/w01-l02-team-setup/practice/console/check_console.py ~/p58-console
```

Скрипт напишет по каждому заданию `OK` или `НЕТ` и подскажет, чего не хватает (задание 8 — бонус, `—` там не ошибка).

Как сдавать:

* покажи вывод самопроверки ментору у экрана и ответь на вопрос по любой команде;
* если GitHub-организация класса уже готова, дополнительно открой PR с `about-<ник>.md` в учебный репозиторий
  класса (ссылку даст ментор).
