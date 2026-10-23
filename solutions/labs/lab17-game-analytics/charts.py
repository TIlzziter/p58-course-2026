"""Задача 2 (продолжение). Честный график DAU."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_dau(series, path, title="Игроков в день (DAU)"):
    """Линейный график series (индекс — даты), сохранить PNG в path и вернуть Figure.

    Честный график: ось Y начинается с 0 (иначе рост с 40 до 44 выглядит как взлёт), подписаны обе оси,
    есть заголовок. После сохранения фигуру не закрывать — тесты её читают."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(list(series.index), list(series.values), marker="o")
    ax.set_ylim(bottom=0)
    ax.set_title(title)
    ax.set_xlabel("день")
    ax.set_ylabel("игроков")
    fig.autofmt_xdate()
    fig.savefig(path, dpi=80)
    return fig
