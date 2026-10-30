# Практика: Консоль и Git руками (урок 02, 30.10)

> Рабочая версия 1 (29.10.2026): план перерабатывается по итогам встреч менторов, часть решений на согласовании и может измениться.

Каждое задание — 5–10 минут. Все команды вводим **руками**: агента можно спросить, что делает команда или
почему ошибка, но команды и скрипты из его ответа не копируем (этап 0, до конца декабря).
В конце запускаете самопроверку `check_console.py` и показываете её вывод ментору.

## Где работаем

Учебные ВМ появятся примерно через 2 недели. Пока:

* **свой ноутбук**: терминал macOS или Linux; на Windows — WSL (Ubuntu) или Git Bash;
* **запасной вариант**, если на ноутбуке не заводится, — GitHub Codespaces: откройте репозиторий курса на GitHub →
  **Code → Codespaces → Create codespace**. Это Linux в браузере, ставить ничего не нужно, нужен аккаунт GitHub.

Нужны `git` и Python 3.12+ (`python3 --version`). Если команда `python` не найдена, пишите `python3`.

## Подготовка: рабочая папка и клон курса

```bash
mkdir -p ~/p58-console && cd ~/p58-console
git clone https://github.com/school58-project/p58-course-labs.git
```

Клон нужен уже в задании 3; остальную работу с Git делаем в задании 6.

## Образец: что должно получиться

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

**1. Навигация.** `pwd`, `ls -la`, `cd`, `mkdir -p`. Соберите дерево `project/` и `sandbox/` по образцу
одной-двумя командами `mkdir -p`. Проверьте `ls -la project` и `ls project/docs`.

**2. Файлы.** В `sandbox/`: `touch draft.txt` → `cp draft.txt copy.txt` → `mv copy.txt notes.txt` → `rm draft.txt`.
Посмотрите README лабораторной 01 через `cat`, `less` (выход — `q`), `head -n 5` и `tail -n 5`.
Итог: в `sandbox/` есть `notes.txt`, а `draft.txt` и `copy.txt` нет.

**3. Потоки.** Найдите все TODO в файлах лабораторной 01 и запишите их в файл, а в конце — их количество:

```bash
LAB=p58-course-labs/lessons/w01-l02-team-setup/labs/lab01-git-flow
grep -rn TODO "$LAB" > sandbox/todo.txt
grep -rn TODO "$LAB" | wc -l >> sandbox/todo.txt
```

Разберитесь, чем `>` отличается от `>>` и что делает `|`. Допишите в `sandbox/notes.txt` одну строку через `echo ... >>`.

**4. Права и скрипты.** Создайте в рабочей папке `hello.sh`: первая строка `#!/usr/bin/env bash`, дальше `echo`,
который печатает приветствие и первый аргумент `$1`. Сделайте файл исполняемым (`chmod +x hello.sh`)
и запустите: `./hello.sh <ник>`. Посмотрите права до и после `chmod` через `ls -la`.

**5. Окружение.** Соберите `env.txt`:

```bash
which python > env.txt              # или which python3
python --version >> env.txt         # или python3 --version
export P58_NICK=<ник>
echo "P58_NICK=$P58_NICK" >> env.txt
history | tail -n 5 >> env.txt
```

**6. Git.** Внутри `p58-course-labs/`:

```bash
git config --global user.name "<ник>"
git config --global user.email "<почта от GitHub>"
git log --oneline | head
git switch -c about/<ник>
```

Создайте `about-<ник>.md` (3–5 строк: ник, какую роль в проекте хотите, чему хотите научиться) и закоммитьте его
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

**8. Бонус дома.** `ssh-keygen -t ed25519`, затем публичный ключ (`cat ~/.ssh/id_ed25519.pub`) добавить в GitHub:
**Settings → SSH and GPG keys**. Пригодится для ВМ. Приватный ключ (`id_ed25519` без `.pub`) никому не показываем.

## Самопроверка и сдача

```bash
python p58-course-labs/lessons/w01-l02-team-setup/practice/console/check_console.py ~/p58-console
```

Скрипт печатает по каждому заданию `OK` или `НЕТ` с подсказкой, чего не хватает (задание 8 — бонус, `—` не ошибка).

Как сдавать:

* покажите вывод самопроверки ментору у экрана и ответьте на вопрос по любой команде;
* если GitHub-организация класса уже готова — дополнительно откройте PR с `about-<ник>.md` в учебный репозиторий
  класса (ссылку даст ментор).
