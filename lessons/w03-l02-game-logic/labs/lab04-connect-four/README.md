# Лабораторная 04. «4 в ряд»

Серверная логика игры 1. Модуль `connect4.py` ничего не знает про HTTP и canvas: это чистые функции и класс
`Game`, которые потом вызовет FastAPI (обработчик хода) и которые легко покрыть тестами. Так мы **отделяем
логику от транспорта и отрисовки**.

Поле — список строк **сверху вниз**: `board[0]` — верхняя строка, `board[5]` — нижняя; `0` — пусто,
`1` и `2` — игроки. В тестах поле удобно рисовать картинкой: см. `board_from` в `tests/conftest.py`.

```bash
python check.py
python check.py -v 4
```

## Задачи

| № | Функция | Что сделать | Что проверить |
|---|---|---|---|
| 1 | `new_board` | Поле `rows × cols` из **независимых** строк; меньше 4×4 — `ValueError`. | `[[0]*7]*6` — ловушка: одна строка, 6 ссылок |
| 2 | `drop` | Фишка падает на **нижнюю** свободную клетку; `MoveError("bad_column")`, `MoveError("column_full")`; игрок только 1 или 2. | вернули номер строки |
| 3 | `legal_moves` | Номера незаполненных столбцов по возрастанию. | столбец полон, если занята верхняя клетка |
| 4 | `winning_line` | Четвёрки по горизонтали, вертикали и **обеим диагоналям**, без «перехода через край». | порядок клеток — от первой найденной клетки по направлению |
| 5 | `status` | `"win1"`, `"win2"`, `"draw"` или `"playing"`. | ничья — поле заполнено без четвёрки |
| 6 | `Game.play`, `undo`, `from_moves` | Смена хода, запрет ходить после конца партии (`game_over`), отмена хода, партия из записи `"4453"` (столбцы с 1). | `nothing_to_undo`, `bad_notation` |
| 7* | `Game.to_json` | Состояние для клиента: `board` (копия!), `turn`, `status`, `win_cells`, `moves`. | клиент подсвечивает `win_cells` |

Подсказка к задаче 4: переберите каждую клетку и 4 направления `(0, 1)`, `(1, 0)`, `(1, 1)`, `(1, -1)`;
четвёрка из клетки `(r, c)` — это клетки `(r + i·dr, c + i·dc)` для `i = 0..3`. Проверяйте, что все они на поле.

## После тестов: подключаем canvas

Минимальный клиент для проверки «глазами» (в проекте он живёт в `web/`):

```html
<canvas id="board" width="350" height="300"></canvas>
<script>
const ctx = document.getElementById("board").getContext("2d");
function draw(state) {                       // state — ответ to_json() от API
  ctx.fillStyle = "#1e3a8a"; ctx.fillRect(0, 0, 350, 300);
  state.board.forEach((row, r) => row.forEach((v, c) => {
    ctx.beginPath(); ctx.arc(25 + c * 50, 25 + r * 50, 20, 0, 2 * Math.PI);
    ctx.fillStyle = ["#0b1020", "#facc15", "#ef4444"][v]; ctx.fill();
  }));
}
document.getElementById("board").onclick = e => {
  const col = Math.floor(e.offsetX / 50);    // столбец по координате клика
  fetch(`/rooms/1/moves`, {method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({column: col})}).then(r => r.json()).then(draw);
};
</script>
```

Обратите внимание: клиент **не решает**, можно ли ходить, — он только отправляет номер столбца и рисует
ответ сервера.
