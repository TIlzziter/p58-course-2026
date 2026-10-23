"""Контест 9 · Тексты, промпты и шаблоны — эталонные решения A1–D3."""
import html
import json
import math
import re

# ---------- A. Строки и токены ----------

def approx_tokens(text: str) -> int:
    """A1. Куски — слова (\\w+) и отдельные знаки (не буква и не пробел); кусок длины L — ceil(L/4) токенов."""
    return sum(math.ceil(len(t) / 4) for t in re.findall(r"\w+|[^\w\s]", text))


def truncate(text: str, limit: int) -> str:
    """A2. Обрезать до limit символов вместе с «…», не разрезая слово."""
    if limit < 2:
        raise ValueError("limit >= 2")
    if len(text) <= limit:
        return text
    cut = text[:limit - 1]
    if not text[limit - 1].isspace() and " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" ,;:—-") + "…"


def wrap(text: str, width: int) -> list[str]:
    """A3. Жадный перенос по словам; слово длиннее width режется на куски по width."""
    words = []
    for w in text.split():
        words += [w[i:i + width] for i in range(0, len(w), width)]
    lines, cur = [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def split_chunks(text: str, size: int, overlap: int) -> list[str]:
    """A4*. Куски для контекста модели: предложения целиком, нахлёст overlap предложений."""
    sentences = [s for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s]
    chunks, cur = [], []
    for s in sentences:
        if cur and len(" ".join([*cur, s])) > size:
            chunks.append(" ".join(cur))
            cur = cur[len(cur) - overlap:] if overlap else []
            while cur and len(" ".join([*cur, s])) > size:
                cur.pop(0)
        cur.append(s)
    if cur:
        chunks.append(" ".join(cur))
    return chunks


# ---------- B. Шаблоны ----------

VAR = re.compile(r"\{\{\s*([\w.]+)((?:\|\w+(?::[^|}]*)?)*)\s*\}\}")
MISSING = object()


def lookup(ctx, name: str):
    cur = ctx
    for part in name.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                return MISSING
            cur = cur[part]
        elif hasattr(cur, part):
            cur = getattr(cur, part)
        else:
            return MISSING
    return cur


def render(template: str, ctx: dict) -> str:
    """B1. Подстановка {{ имя }} и {{ a.b.c }}; нет значения — KeyError(имя)."""
    def sub(m):
        if m.group(2):
            raise ValueError("фильтры — в B2")
        v = lookup(ctx, m.group(1))
        if v is MISSING:
            raise KeyError(m.group(1))
        return str(v)
    return VAR.sub(sub, template)


def apply_filter(value, name: str, arg: str | None):
    if name == "default":
        return arg if value is MISSING or value is None or value == "" else value
    if value is MISSING:
        raise KeyError("missing")
    if name == "upper":
        return str(value).upper()
    if name == "pad":
        return str(value).rjust(int(arg))
    if name == "escape":
        return html.escape(str(value))
    if name == "plural":
        one, few, many = arg.split(",")
        n = abs(int(value))
        if n % 10 == 1 and n % 100 != 11:
            form = one
        elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            form = few
        else:
            form = many
        return f"{value} {form}"
    raise ValueError(f"фильтр {name}")


def render_filters(template: str, ctx: dict) -> str:
    """B2. Как B1, плюс фильтры: upper, pad:N, escape, default:текст, plural:одна,две,пять."""
    def sub(m):
        name, chain = m.group(1), m.group(2)
        v = lookup(ctx, name)
        for f in re.findall(r"\|(\w+)(?::([^|}]*))?", chain):
            fname, arg = f[0], f[1].strip() or None
            try:
                v = apply_filter(v, fname, arg)
            except KeyError:
                raise KeyError(name) from None
        if v is MISSING:
            raise KeyError(name)
        return str(v)
    return VAR.sub(sub, template)


FOR = re.compile(r"\{%\s*for (\w+) in ([\w.]+)\s*%\}(.*?)\{%\s*endfor\s*%\}", re.DOTALL)


def render_for(template: str, ctx: dict) -> str:
    """B3. Циклы {% for x in items %}…{% endfor %} (не вложенные) + B2; внутри — loop.index, loop.last."""
    out, pos = [], 0
    for m in FOR.finditer(template):
        out.append(render_filters(template[pos:m.start()], ctx))
        var, src, body = m.groups()
        items = lookup(ctx, src)
        if items is MISSING:
            raise KeyError(src)
        items = list(items)
        for i, item in enumerate(items, 1):
            local = {**ctx, var: item, "loop": {"index": i, "last": i == len(items)}}
            out.append(render_filters(body, local))
        pos = m.end()
    out.append(render_filters(template[pos:], ctx))
    return "".join(out)


# ---------- C. Промпты ----------

PLACE = re.compile(r"\{\{|\}\}|\{(\w+)\}")


def fill_prompt(template: str, values: dict) -> tuple[str, list[str], list[str]]:
    """C1. Плейсхолдеры {имя}; {{ и }} — буквальные скобки. Ответ: (текст, нет значения, лишние значения)."""
    used, missing = set(), set()

    def sub(m):
        tok = m.group(0)
        if tok == "{{":
            return "{"
        if tok == "}}":
            return "}"
        name = m.group(1)
        if name in values:
            used.add(name)
            return str(values[name])
        missing.add(name)
        return tok
    text = PLACE.sub(sub, template)
    return text, sorted(missing), sorted(set(values) - used)


def words(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.lower()))


def jaccard(a: str, b: str) -> float:
    wa, wb = words(a), words(b)
    return len(wa & wb) / len(wa | wb) if wa | wb else 0.0


def few_shot(examples: list[tuple[str, str]], query: str, k: int) -> str:
    """C2. k самых похожих примеров (Жаккар по словам), при равенстве — раньше в списке."""
    order = sorted(range(len(examples)), key=lambda i: (-jaccard(examples[i][0], query), i))[:k]
    parts = [f"Вопрос: {examples[i][0]}\nОтвет: {examples[i][1]}" for i in order]
    parts.append(f"Вопрос: {query}\nОтвет:")
    return "\n\n".join(parts)


def extract_json(text: str) -> list[dict]:
    """C3. Все JSON-объекты верхнего уровня в тексте ответа модели (скобки внутри строк не считаются)."""
    found, i, n = [], 0, len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        depth, j, in_str, esc = 0, i, False, False
        end = -1
        while j < n:
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
            j += 1
        if end == -1:
            i += 1
            continue
        try:
            obj = json.loads(text[i:end + 1])
        except json.JSONDecodeError:
            i += 1
            continue
        found.append(obj)
        i = end + 1
    return found


def diff_lines(a: str, b: str) -> list[str]:
    """C4*. Построчный diff через наибольшую общую подпоследовательность."""
    x, y = a.splitlines(), b.splitlines()
    n, m = len(x), len(y)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = dp[i + 1][j + 1] + 1 if x[i] == y[j] else max(dp[i + 1][j], dp[i][j + 1])
    out, i, j = [], 0, 0
    while i < n and j < m:
        if x[i] == y[j]:
            out.append("  " + x[i])
            i += 1
            j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            out.append("- " + x[i])
            i += 1
        else:
            out.append("+ " + y[j])
            j += 1
    out += ["- " + s for s in x[i:]] + ["+ " + s for s in y[j:]]
    return out


# ---------- D. Проверка ответов ----------

def levenshtein(a: str, b: str) -> int:
    """D1. Расстояние редактирования: вставка, удаление, замена — по 1."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def normalize_answer(s: str) -> str:
    s = s.lower().replace("ё", "е")
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())


def fuzzy_match(answer: str, expected: str, tolerance: float = 0.2) -> bool:
    """D2. Нормализация, затем расстояние не больше int(tolerance · длина нормализованного эталона)."""
    a, e = normalize_answer(answer), normalize_answer(expected)
    return levenshtein(a, e) <= int(tolerance * len(e))


def pass_at_k(n: int, c: int, k: int) -> float:
    """D3. Несмещённая оценка pass@k: 1 − C(n−c, k) / C(n, k), округлить до 4 знаков."""
    if not (0 <= c <= n and 1 <= k <= n):
        raise ValueError("нужно 0 <= c <= n и 1 <= k <= n")
    if n - c < k:
        return 1.0
    return round(1 - math.comb(n - c, k) / math.comb(n, k), 4)
