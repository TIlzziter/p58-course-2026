from datetime import date

import matplotlib
from analytics import dau
from charts import plot_dau

matplotlib.use("Agg")


def test_dau(small_df):
    s = dau(small_df)
    assert s.name == "dau"
    assert list(s.index) == [date(2027, 3, d) for d in range(1, 9)]
    assert list(s) == [2, 2, 0, 2, 0, 0, 0, 1]


def test_plot(small_df, tmp_path):
    p = tmp_path / "dau.png"
    fig = plot_dau(dau(small_df), p)
    assert p.exists() and p.read_bytes()[:4] == b"\x89PNG"
    ax = fig.axes[0]
    assert ax.get_ylim()[0] == 0
    assert ax.get_title() and ax.get_xlabel() and ax.get_ylabel()
    assert len(ax.lines) == 1 and len(ax.lines[0].get_xdata()) == 8
