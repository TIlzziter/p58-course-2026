# Лабораторная 14. Разбор логов и алерты

Сервер на проде — чёрный ящик, пока он не пишет логи и метрики. Сегодня: логи одной строкой JSON, которые можно
фильтровать; метрики RED (Rate, Errors, Duration) и гистограмма в формате Prometheus; алерт, который не
срабатывает от одного всплеска; уведомления в Telegram без спама. В `sample/incident.log` — логи десяти минут
с настоящим (учебным) инцидентом, на них удобно проверять себя.

```bash
python check.py           # все задачи
python check.py -v 4      # подробности по задаче 4
```

| Файл | Задачи |
|---|---|
| `logs.py` | 1 разбор и фильтр логов, 2 `JsonFormatter` для `logging` |
| `metrics.py` | 3 RED за окно, 4 гистограмма и квантиль |
| `alerts.py` | 5 правило с `for`, 6 уведомления без спама |
| `incident.py` | 7* сводка инцидента |

## Задачи

| № | Что сделать |
|---|---|
| 1 | `parse_line`: не JSON, не объект, нет `ts` или чужой `level` — `None`, без исключений. `filter_logs(lines, level, **fields)`: уровни сравниваем по порядку `LEVELS`, а не как строки (`"ERROR" < "INFO"` по алфавиту!). |
| 2 | `JsonFormatter`: ключи `ts` (UTC, ISO 8601 с миллисекундами), `level`, `logger`, `msg` (через `record.getMessage()`), затем поля из `extra=` по алфавиту, затем `exc`. Кириллица без `\u`. Несериализуемое — через `str`. Подсказка: стандартные поля `LogRecord` можно получить из пустой записи `logging.LogRecord(...)`. |
| 3 | `percentile` — ближайший ранг. `red(records, start, end)`: окно `[start, end)`, ошибки — только `5xx`, пустое окно — `None`. |
| 4 | `Histogram`: граница корзины **включается** (`v <= le`), `render()` — накопленные счётчики, включая `+Inf`, потом `_sum` и `_count`. `quantile(q)` — как `histogram_quantile` в Prometheus: найти корзину, где накопленный счёт ≥ `q·count`, и интерполировать линейно между её границами (нижняя у первой — 0); в `+Inf` — верхняя конечная граница. |
| 5 | `evaluate(samples, threshold, for_s)`: условие `value > threshold`; алерт **горит**, когда условие держится непрерывно `≥ for_s` секунд (от первого замера выше порога); замер не выше порога сбрасывает ожидание и, если горело, даёт `resolved`. |
| 6 | `Notifier.process(ts, firing)` — `firing` — набор горящих сейчас. Новые: `🔴 <b>имя</b>`; горят дольше `repeat_s` с прошлого сообщения: `🔁 <b>имя</b> — всё ещё горит`; погасли: `✅ <b>имя</b> — решено`. Порядок: новые, повторы, решённые, внутри — по имени. Имя экранируем `html.escape`: сообщение уходит с `parse_mode=HTML`. |
| 7* | `incident_summary(records, ratio, min_requests)` — по docstring. Проверьте себя на `sample/incident.log`. |

## Как это подключается в проекте

```python
# логи: один раз при старте
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger("game.http")

@app.middleware("http")
async def access_log(request, call_next):
    t = time.perf_counter()
    response = await call_next(request)
    ms = round((time.perf_counter() - t) * 1000)
    log.info("request", extra={"path": request.url.path, "status": response.status_code, "ms": ms})
    return response
```

```python
# алерт в Telegram: отдельный бот и чат команды, токен — из переменной окружения
async def send_alert(text: str) -> None:
    url = f"https://api.telegram.org/bot{os.environ['ALERT_BOT_TOKEN']}/sendMessage"
    async with httpx.AsyncClient(timeout=5) as c:
        await c.post(url, json={"chat_id": os.environ["ALERT_CHAT_ID"], "text": text, "parse_mode": "HTML"})
```

Не пишите в логи токены, `initData` целиком и личные данные: логи читают многие, а хранятся они долго.
